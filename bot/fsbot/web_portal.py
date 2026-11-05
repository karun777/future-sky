"""Opt-in, authenticated walking web pilot; runs on the existing bot event loop.

No player selection parameter, state-file access, command invocation or public bind.
Authlib owns OAuth2 protocol handling. This module owns short-lived opaque sessions.
"""
import asyncio
from dataclasses import dataclass, field
import hmac
import hashlib
import json
import logging
from pathlib import Path
import secrets
import time
from urllib.parse import urlencode

from aiohttp import web
from fsbot.web_character_view import character_view, CharacterAccessDenied

ORIGIN = "https://future-sky.net"
CALLBACK = ORIGIN + "/play/auth/callback"
LOGIN_COOKIE = "__Host-fs-login"
SESSION_COOKIE = "__Host-fs-session"
STATIC = Path(__file__).with_name("web_static")
SESSION_SECONDS = 8 * 60 * 60
PENDING_SECONDS = 5 * 60
MAX_RECORDS = 1000


@dataclass(frozen=True)
class WebConfig:
    client_id: str
    client_secret: str = field(repr=False)
    allowed_ids: frozenset = frozenset()

    def __post_init__(self):
        if not self.client_id.isascii() or not self.client_id.isdecimal():
            raise ValueError("A Discord client ID is required")
        if not self.client_secret or not self.allowed_ids:
            raise ValueError("OAuth secret and pilot allowlist are required")
        if any(not isinstance(uid, str) or not uid.isascii()
               or not uid.isdecimal() for uid in self.allowed_ids):
            raise ValueError("Pilot entries must be Discord user IDs")


class DiscordOAuth:
    """Library-backed authorization-code flow. Tokens never reach the browser."""
    def __init__(self, config):
        from authlib.integrations.httpx_client import AsyncOAuth2Client
        self.client_type = AsyncOAuth2Client
        self.config = config

    def client(self, **kwargs):
        return self.client_type(
            self.config.client_id, self.config.client_secret,
            scope="identify", redirect_uri=CALLBACK,
            token_endpoint_auth_method="client_secret_post",
            timeout=10.0, **kwargs)

    async def authorize(self):
        async with self.client() as client:
            return client.create_authorization_url(
                "https://discord.com/oauth2/authorize")

    async def identity(self, code, state):
        # Construct from fixed origin, never forwarded Host/request URL.
        response_url = CALLBACK + "?" + urlencode({"code": code, "state": state})
        async with self.client(state=state) as client:
            await client.fetch_token(
                "https://discord.com/api/oauth2/token",
                authorization_response=response_url)
            response = await client.get("https://discord.com/api/v10/users/@me")
            response.raise_for_status()
            data = response.json()
            uid = data.get("id")
            if not isinstance(uid, str) or not uid.isascii() or not uid.isdecimal():
                raise ValueError("Invalid identity response")
            return uid


def cookie(response, name, value, max_age):
    response.set_cookie(name, value, max_age=max_age, secure=True,
                        httponly=True, samesite="Lax", path="/")


def create_app(bot, config, *, oauth=None, clock=time.monotonic):
    provider = oauth or DiscordOAuth(config)
    pending, sessions = {}, {}

    def prune(records):
        for key in tuple(records):
            if records[key]["expires"] <= clock():
                del records[key]

    def session(request):
        prune(sessions)
        value = sessions.get(request.cookies.get(SESSION_COOKIE, ""))
        if value is None:
            raise web.HTTPUnauthorized(text="Sign in through Discord.")
        return value

    @web.middleware
    async def headers(request, handler):
        try:
            response = await handler(request)
        except web.HTTPException as exc:
            response = web.Response(status=exc.status, body=exc.body, headers=exc.headers)
        response.headers.update({
            "Cache-Control": "no-store",
            "Referrer-Policy": "no-referrer",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy":
                "default-src 'none'; script-src 'self'; style-src 'self'; "
                "img-src 'self'; connect-src 'self'; form-action 'self'; "
                "frame-ancestors 'none'; base-uri 'none'",
        })
        return response

    async def index(request):
        return web.Response(text=(STATIC / "index.html").read_text(),
                            content_type="text/html")

    async def asset(request):
        name = request.match_info["name"]
        if name not in {"game.css", "game.js"}:
            raise web.HTTPNotFound()
        content_type = "text/css" if name.endswith("css") else "application/javascript"
        return web.Response(text=(STATIC / name).read_text(), content_type=content_type)

    async def login(request):
        prune(pending)
        if len(pending) >= MAX_RECORDS:
            raise web.HTTPTooManyRequests(text="Please try again shortly.")
        try:
            url, state = await provider.authorize()
        except Exception:
            raise web.HTTPServiceUnavailable(text="Discord login is unavailable.") from None
        nonce = secrets.token_urlsafe(32)
        pending[nonce] = {"state": state, "expires": clock() + PENDING_SECONDS}
        response = web.Response(status=302, headers={"Location": url})
        cookie(response, LOGIN_COOKIE, nonce, PENDING_SECONDS)
        return response

    async def callback(request):
        prune(pending)
        record = pending.pop(request.cookies.get(LOGIN_COOKIE, ""), None)
        state = request.query.get("state", "")
        if (record is None or not state
                or len(request.query.getall("state", [])) != 1
                or not hmac.compare_digest(record["state"].encode(), state.encode())):
            raise web.HTTPBadRequest(text="Login expired or invalid. Start again.")
        code = request.query.get("code", "")
        if request.query.get("error") or not code or len(request.query.getall("code", [])) != 1:
            raise web.HTTPBadRequest(text="Discord login was not completed.")
        try:
            uid = await asyncio.wait_for(provider.identity(code, state), timeout=15)
        except Exception:
            raise web.HTTPBadGateway(text="Discord identity could not be verified.") from None
        if uid not in config.allowed_ids or not isinstance(bot.storage.characters.get(uid), dict):
            raise web.HTTPForbidden(text="This pilot is limited to its existing authorised character.")
        prune(sessions)
        old = request.cookies.get(SESSION_COOKIE, "")
        sessions.pop(old, None)
        if len(sessions) >= MAX_RECORDS:
            raise web.HTTPTooManyRequests(text="Please try again shortly.")
        token = secrets.token_urlsafe(32)
        sessions[token] = {"uid": uid, "csrf": secrets.token_urlsafe(32),
                           "expires": clock() + SESSION_SECONDS}
        response = web.Response(status=302, headers={"Location": "/play/"})
        cookie(response, LOGIN_COOKIE, "", 0)
        cookie(response, SESSION_COOKIE, token, SESSION_SECONDS)
        return response

    def current_view(value):
        if not bot.is_ready():
            raise web.HTTPServiceUnavailable(text="Game connection is recovering.")
        try:
            view = character_view(bot.storage, value["uid"],
                                  allowed_discord_ids=config.allowed_ids)
        except CharacterAccessDenied:
            raise web.HTTPForbidden(text="Character unavailable.")
        view["session"] = {"csrf": value["csrf"]}
        return view

    def navigation():
        return bot.get_cog("NavigationCog") if hasattr(bot, "get_cog") else None

    def add_walking(view, value):
        nav = navigation()
        if nav is None:
            return
        uid = value["uid"]
        room_id = view["location"]["id"]
        room = bot.storage.rooms.get(room_id, {})
        ch = bot.storage.characters[uid]
        refusal = nav.walking_refusal(uid, web_pilot=True)
        from fsbot.pod_opening import pod_bearings, GUIDANCE
        description = ""
        exits = []
        if room_id and isinstance(room, dict):
            description = room.get("description", "")
            if not isinstance(description, str):
                description = ""
            bearings = pod_bearings(ch)
            if bearings:
                description = bearings + "\n\n" + GUIDANCE
            raw = room.get("exits", {})
            if not refusal and isinstance(raw, dict):
                exits = [direction for direction, target in raw.items()
                         if isinstance(direction, str) and len(direction) <= 40
                         and isinstance(target, str) and target in bot.storage.rooms]
        # Only current visible direction names, never a raw room/map export.
        view["location"]["description"] = description
        view["walking"] = {"exits": exits, "notice": refusal or ""}
        view["capabilities"] = {"read_only": False, "actions": ["walk"]}
        revision = nav.walk_revision(uid)
        offer = value.get("walk_offer")
        if not (offer and offer["expires"] > clock() + 10
                and offer["room"] == room_id and offer["revision"] == revision
                and offer["exits"] == exits):
            offer = {"token": secrets.token_urlsafe(32), "room": room_id,
                     "revision": revision, "exits": exits, "expires": clock() + 120}
            value["walk_offer"] = offer
        view["walking"]["token"] = offer["token"]
        # Curated current status only, not raw idle records, private source
        # message IDs, history or a claim about the cause of every room change.
        from fsbot.idle_home import record as idle_record
        try:
            idle = idle_record(ch)
        except (ValueError, TypeError, AttributeError):
            idle = None
        view["idle_home"] = {
            "enabled": bool(idle and idle["enabled"]),
            "status": idle.get("status") if idle and idle.get("status") in {"armed", "walking", "home", "blocked", "disabled"} else None,
            "at_home": bool(idle and not ch.get("in_cube") and room_id == idle["home"]),
        }

    def inspection_stamp(uid):
        ch = bot.storage.characters[uid]
        nav = navigation()
        revision = nav.walk_revision(uid) if nav else None
        # Private comparison only; no raw state or fingerprint reaches the client.
        return hashlib.sha256(json.dumps(
            [ch, revision], sort_keys=True, default=str).encode()).hexdigest()

    def inspection_refusal(uid):
        nav = navigation()
        if nav is None:
            return "Inspection is unavailable while the game connection recovers."
        refusal = nav.walking_refusal(uid, web_pilot=True)
        if refusal:
            return refusal
        if uid in getattr(nav, "walking", set()):
            return "Another movement is finishing. Wait, then inspect."
        ch = bot.storage.characters[uid]
        from fsbot.pod_opening import opening_state
        if ch.get("current_room") != "pod_room":
            return "This first inspection pilot is available in the pod."
        if not opening_state(ch):
            return "Begin finding your bearings with !awaken in Discord."
        return None

    def add_inspection(view, value):
        from fsbot.pod_inspection import web_targets
        uid = value["uid"]
        refusal = inspection_refusal(uid)
        targets = [] if refusal else web_targets(bot.storage.characters[uid])
        stamp = inspection_stamp(uid)
        offer = value.get("inspect_offer")
        if not (offer and offer["expires"] > clock() + 10
                and offer["stamp"] == stamp and offer["targets"] == targets):
            offer = {"token": secrets.token_urlsafe(32), "stamp": stamp,
                     "targets": targets, "expires": clock() + 120}
            value["inspect_offer"] = offer
        view["inspection"] = {"targets": targets, "notice": refusal or "",
                              "token": offer["token"]}

    async def inspect(request):
        value = session(request)
        supplied = request.headers.get("X-CSRF-Token", "")
        if (request.headers.get("Origin") != ORIGIN or not supplied
                or not hmac.compare_digest(value["csrf"].encode(), supplied.encode())):
            raise web.HTTPForbidden(text="Invalid inspection request.")
        current_view(value)
        try:
            body = await request.json()
        except (ValueError, UnicodeDecodeError):
            raise web.HTTPBadRequest(text="Invalid inspection request.") from None
        if (not isinstance(body, dict) or set(body) != {"target", "token"}
                or not isinstance(body["target"], str) or not isinstance(body["token"], str)
                or len(body["target"]) > 40 or len(body["token"]) > 128):
            raise web.HTTPBadRequest(text="Choose one visible detail.")
        offer = value.get("inspect_offer")
        if (not offer or offer["expires"] <= clock()
                or not hmac.compare_digest(offer["token"].encode(), body["token"].encode())):
            raise web.HTTPConflict(text="That inspection expired or was already used. Refresh.")
        if body["target"] not in offer["targets"]:
            raise web.HTTPBadRequest(text="Choose one visible detail.")
        value.pop("inspect_offer", None)
        uid = value["uid"]
        refusal = inspection_refusal(uid)
        if refusal:
            raise web.HTTPConflict(text=refusal)
        if offer["stamp"] != inspection_stamp(uid):
            raise web.HTTPConflict(text="Your situation changed. Refresh before inspecting.")
        # Explicit attention interrupts idle return. No await between final
        # validation, activity recording and the durable shared observation.
        idle = bot.get_cog("IdleHomeCog")
        if idle:
            idle.observe(uid)
            if uid in idle.suspended:
                raise web.HTTPServiceUnavailable(text="Your activity could not be saved.")
        from fsbot.pod_inspection import inspect_pod
        try:
            observation = inspect_pod(bot.storage, uid, body["target"])
        except (ValueError, TypeError, AttributeError):
            raise web.HTTPConflict(text="That detail is unavailable. Refresh.") from None
        except Exception:
            logging.getLogger("futuresky.web").exception("Inspection save failed")
            raise web.HTTPServiceUnavailable(text="Inspection could not be saved. Refresh before trying again.") from None
        # Same saved knowledge is visible to Discord without unsolicited chatter.
        value.pop("walk_offer", None)
        return web.json_response({"ok": True, "observation": observation})

    def wardrobe_projection(uid):
        from fsbot.web_wardrobe import wardrobe_view
        from fsbot.cogs.wardrobe import load_catalogue
        refusal = inspection_refusal(uid)
        if refusal or bot.get_cog("CoreCog") is None:
            return {"available": False, "options": [], "actions": [],
                    "notice": refusal or "Equipment is unavailable."}
        return wardrobe_view(bot.storage.characters[uid], bot.storage.items_db, load_catalogue())

    def add_wardrobe(view, value):
        uid = value["uid"]
        projection = wardrobe_projection(uid)
        stamp = inspection_stamp(uid)
        offer = value.get("wardrobe_offer")
        actions = projection.pop("actions")
        if not (offer and offer["expires"] > clock() + 10
                and offer["stamp"] == stamp and offer["actions"] == actions):
            offer = {"token": secrets.token_urlsafe(32), "stamp": stamp,
                     "actions": actions, "expires": clock() + 120}
            value["wardrobe_offer"] = offer
        view["wardrobe"] = {**projection, "token": offer["token"]}

    async def wardrobe_action(request):
        value = session(request)
        supplied = request.headers.get("X-CSRF-Token", "")
        if (request.headers.get("Origin") != ORIGIN or not supplied
                or not hmac.compare_digest(value["csrf"].encode(), supplied.encode())):
            raise web.HTTPForbidden(text="Invalid wardrobe request.")
        current_view(value)
        try:
            body = await request.json()
        except (ValueError, UnicodeDecodeError):
            raise web.HTTPBadRequest(text="Invalid wardrobe request.") from None
        if (not isinstance(body, dict) or set(body) != {"action", "token"}
                or not isinstance(body["action"], str) or not isinstance(body["token"], str)
                or len(body["action"]) > 160 or len(body["token"]) > 128):
            raise web.HTTPBadRequest(text="Choose one available garment action.")
        offer = value.get("wardrobe_offer")
        if (not offer or offer["expires"] <= clock()
                or not hmac.compare_digest(offer["token"].encode(), body["token"].encode())):
            raise web.HTTPConflict(text="That wardrobe choice expired. Refresh.")
        if body["action"] not in offer["actions"]:
            raise web.HTTPBadRequest(text="That garment action is unavailable.")
        value.pop("wardrobe_offer", None)
        uid = value["uid"]
        refusal = inspection_refusal(uid)
        if refusal:
            raise web.HTTPConflict(text=refusal)
        if offer["stamp"] != inspection_stamp(uid):
            raise web.HTTPConflict(text="Your situation changed. Review the wardrobe again.")
        if body["action"] not in wardrobe_projection(uid)["actions"]:
            raise web.HTTPConflict(text="That garment is no longer available.")
        idle = bot.get_cog("IdleHomeCog")
        if idle:
            idle.observe(uid)
            if uid in idle.suspended:
                raise web.HTTPServiceUnavailable(text="Your activity could not be saved.")
        # No await between final validation and shared durable mutation.
        from fsbot.web_wardrobe import select_outfit
        from fsbot.cogs.wardrobe import load_catalogue
        from fsbot.dressing import resolve_clothing
        action, key = body["action"].split(":", 1)
        try:
            if action == "select":
                fit = select_outfit(bot.storage, uid, key, load_catalogue())
                message = "You step into " + fit["label"] + ". Your choice is recorded."
            else:
                core = bot.get_cog("CoreCog")
                item, slot = resolve_clothing(bot.storage.characters[uid], bot.storage.items_db, key)
                message = core.equip_item(uid, item, slot)
        except ValueError as exc:
            raise web.HTTPConflict(text=str(exc)) from None
        except Exception:
            logging.getLogger("futuresky.web").exception("Wardrobe action failed")
            raise web.HTTPServiceUnavailable(text="The wardrobe could not save that action.") from None
        value.pop("walk_offer", None)
        value.pop("inspect_offer", None)
        return web.json_response({"ok": True, "message": message})

    async def me(request):
        value = session(request)
        view = current_view(value)
        add_walking(view, value)
        add_inspection(view, value)
        add_wardrobe(view, value)
        return web.json_response(view)

    async def walk(request):
        value = session(request)
        supplied = request.headers.get("X-CSRF-Token", "")
        if (request.headers.get("Origin") != ORIGIN or not supplied
                or not hmac.compare_digest(value["csrf"].encode(), supplied.encode())):
            raise web.HTTPForbidden(text="Invalid movement request.")
        current_view(value)  # Recheck allowlist, existing owner and readiness.
        try:
            body = await request.json()
        except (ValueError, UnicodeDecodeError):
            raise web.HTTPBadRequest(text="Invalid movement request.") from None
        if (not isinstance(body, dict) or set(body) != {"direction", "token"}
                or not isinstance(body["direction"], str)
                or not isinstance(body["token"], str)):
            raise web.HTTPBadRequest(text="Choose one current exit.")
        offer = value.get("walk_offer")
        if (offer is None or offer["expires"] <= clock()
                or not hmac.compare_digest(offer["token"].encode(), body["token"].encode())):
            raise web.HTTPConflict(text="That view expired or was already used. Refresh.")
        if body["direction"] not in offer["exits"]:
            raise web.HTTPBadRequest(text="Choose one current exit.")
        # Consume synchronously before any action await. Replays cannot move twice.
        value.pop("walk_offer", None)
        nav = navigation()
        if nav is None:
            raise web.HTTPServiceUnavailable(text="Movement unavailable.")
        try:
            result = await nav.web_walk(
                value["uid"], body["direction"], expected_room=offer["room"],
                expected_revision=offer["revision"])
        except Exception:
            logging.getLogger("futuresky.web").exception("Walking request failed")
            raise web.HTTPServiceUnavailable(
                text="Movement could not complete. Refresh to check your location.") from None
        # Do not mint another movement offer here; a fresh GET is deliberate.
        return web.json_response(result, status=200 if result["ok"] else 409)

    async def logout(request):
        value = session(request)
        supplied = request.headers.get("X-CSRF-Token", "")
        if (request.headers.get("Origin") != ORIGIN or not supplied
                or not hmac.compare_digest(value["csrf"].encode(), supplied.encode())):
            raise web.HTTPForbidden(text="Invalid sign-out request.")
        sessions.pop(request.cookies.get(SESSION_COOKIE, ""), None)
        response = web.Response(status=204)
        cookie(response, SESSION_COOKIE, "", 0)
        return response

    app = web.Application(middlewares=[headers], client_max_size=4096)
    app.add_routes([
        web.get("/play/", index),
        web.get("/play/static/{name}", asset),
        web.get("/play/auth/discord", login),
        web.get("/play/auth/callback", callback),
        web.get("/play/api/me", me),
        web.post("/play/logout", logout),
        web.post("/play/api/walk", walk),
        web.post("/play/api/inspect", inspect),
        web.post("/play/api/wardrobe", wardrobe_action),
    ])
    return app
