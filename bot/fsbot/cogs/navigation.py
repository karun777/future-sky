# fsbot/cogs/navigation.py — Navigation + Look + Movement (Event Model) v3.8.0
#
# v3.8.0 refactor goals:
# - Route all room-membership queries through bot.presence
# - Remove Navigation's dependency on GameState.get_players_in_room()
# - Preserve all existing movement, rendering, entanglement, and EventBus behaviour
#
# Earlier v3.6.4 goals retained:
# - Keep v3.6.3 behavior:
#     - ThreadNodesCog on_enter triggers fire through `character.entered_room`
#     - If a node entangles, present it and avoid re-render spam
# - Add "walkable entanglement" rule:
#     - If active thread node has `allows_movement: true`, DO NOT block movement
#       (still allows !look to re-present the moment if you want, but GO/TELEPORT should work)
# - Keep contract alignment:
#     - Sneak state lives at ch["extra"]["status"]["sneaking"]
#     - Return echo flag lives at ch["extra"]["status"]["pending_return_echo"]
#     - Thread node state lives ONLY at ch["extra"]["thread_nodes"]
# - Harden against legacy drift:
#     - Migrate old top-level flags (pending_return_echo / sneaking) into extra.status
#
# Event Model:
# - Navigation owns movement and publishes `character.entered_room` after persistence.
# - Narrator reacts only through the EventBus; Navigation no longer knows Narrator exists.
# - Thread Nodes react to room entry only through the EventBus. Navigation still reads
#   entanglement state for movement and presentation sequencing.
#
# Notes:
# - Room broadcast uses each player's run channel via ensure_player_run_channel().

from __future__ import annotations

import random
from typing import Optional, Set, List, Dict, Any, Tuple

import discord
from discord.ext import commands

from fsbot.cogs.router import ensure_player_run_channel
from fsbot.events import create_event


# ============================================================
# Thread Nodes helpers
# ============================================================

def _get_threadnodes_cog(bot):
    try:
        return bot.get_cog("ThreadNodesCog")
    except Exception:
        return None


def _active_thread_node_id(ch: Dict[str, Any]) -> Optional[str]:
    try:
        extra = ch.get("extra")
        if not isinstance(extra, dict):
            return None
        tn = extra.get("thread_nodes")
        if not isinstance(tn, dict):
            return None
        active = tn.get("active_thread_node")
        return str(active) if active else None
    except Exception:
        return None


def _is_entangled(bot, ch: Dict[str, Any]) -> bool:
    """
    True if the character is in a protected narrative moment.

    Contract: thread node state lives only at ch["extra"]["thread_nodes"].
    We treat either an active thread node OR a future encounter container as entangled.

    Walkable entanglement:
    - If the active node defines `allows_movement: true`, movement is NOT blocked.
    """
    try:
        extra = ch.get("extra")
        if not isinstance(extra, dict):
            return False

        tn_state = extra.get("thread_nodes")
        if not isinstance(tn_state, dict):
            return False

        active = tn_state.get("active_thread_node")
        if active:
            node_id = str(active)
            tn = _get_threadnodes_cog(bot)
            node = None
            if tn is not None and hasattr(tn, "nodes"):
                try:
                    node = getattr(tn, "nodes", {}).get(node_id)
                except Exception:
                    node = None

            if isinstance(node, dict) and bool(node.get("allows_movement", False)):
                return False

            return True

        # future-proof: multiplayer encounter container
        if tn_state.get("active_encounter_id"):
            return True

    except Exception:
        return False

    return False


async def _present_entanglement_if_any(bot, ctx: commands.Context, user_id: str) -> bool:
    """
    If entangled, re-present the active narrative prompt and return True.

    Note:
    - This is used mainly by LOOK and post-enter logic to avoid spamming room renders.
    - Movement blocking is handled by checking _is_entangled(bot, ch) where needed.
    """
    try:
        s = getattr(bot, "storage", None)
        if not s:
            return False
        ch = s.characters.get(str(user_id))
        if not isinstance(ch, dict) or not _is_entangled(bot, ch):
            return False

        tn = _get_threadnodes_cog(bot)
        if tn:
            for meth in ("present_active_node", "present_active", "reprint_active_node", "show_active_node"):
                if hasattr(tn, meth):
                    await getattr(tn, meth)(ctx, str(user_id))  # type: ignore[misc]
                    return True

        await ctx.send("🧷 You’re **Entangled** — a narrative moment is active. Use `!answer ...` to continue.")
        return True
    except Exception:
        return False



def _has_unlocked_command(ch: Dict[str, Any], cmd: str) -> bool:
    """True if character flags explicitly unlock a command."""
    try:
        flags = ch.get("flags")
        if not isinstance(flags, dict):
            return False
        unlocked = flags.get("unlocked_commands") or []
        if not isinstance(unlocked, list):
            return False
        want = (cmd or "").strip().lower()
        if not want:
            return False
        for x in unlocked:
            if str(x).strip().lower() == want:
                return True
    except Exception:
        return False
    return False


async def _publish_character_entered_room(
    bot,
    *,
    user_id: str,
    from_room_id: str,
    to_room_id: str,
    movement_type: str,
    direction: Optional[str] = None,
    sneaking: bool = False,
) -> None:
    """Publish the persisted room-entry fact. Navigation remains authoritative."""
    events = getattr(bot, "events", None)
    if events is None:
        return

    try:
        era = bot.state.resolve_era_for_room(to_room_id)
        event = create_event(
            event_type="character.entered_room",
            source_system="navigation",
            actor_id=str(user_id),
            world_time=int(getattr(bot.state, "world_time_seconds", 0)),
            scope={
                "world_id": "future_sky",
                "era": era,
                "room_id": str(to_room_id),
                "scenario_id": None,
                "chapter_id": None,
            },
            payload={
                "from_room_id": str(from_room_id),
                "to_room_id": str(to_room_id),
                "movement_type": str(movement_type),
                "direction": str(direction) if direction else None,
                "sneaking": bool(sneaking),
            },
        )
        await events.publish(event)
    except Exception:
        # Event publication must never invalidate already-persisted movement.
        # EventBus logs subscriber failures; this guard covers wiring/construction faults.
        return

# ============================================================
# Permissions
# ============================================================

def is_dpc(ctx: commands.Context) -> bool:
    if getattr(ctx.author, "guild_permissions", None) and ctx.author.guild_permissions.administrator:
        return True
    role = discord.utils.get(getattr(ctx.author, "roles", []), name="DPC")
    return role is not None


# ============================================================
# Cog
# ============================================================

class NavigationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --------------------------------------------------
    # Contract helpers + legacy migration
    # --------------------------------------------------

    def _status_get(self, ch: Dict[str, Any]) -> Dict[str, Any]:
        """Return extra.status dict if present, else {} (non-creating)."""
        extra = ch.get("extra")
        if isinstance(extra, dict):
            st = extra.get("status")
            if isinstance(st, dict):
                return st
        return {}

    def _status_ensure(self, ch: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure ch.extra.status exists and return it."""
        if not isinstance(ch.get("extra"), dict):
            ch["extra"] = {}
        extra = ch["extra"]
        if not isinstance(extra.get("status"), dict):
            extra["status"] = {}
        return extra["status"]

    def _status_set(self, ch: Dict[str, Any], key: str, value: Any) -> None:
        st = self._status_ensure(ch)
        st[key] = value

    def _migrate_legacy_flags(self, ch: Dict[str, Any]) -> bool:
        """
        Migrate legacy top-level flags into contract-aligned extra.status.
        Returns True if any mutation occurred.
        """
        changed = False
        st = self._status_ensure(ch)

        # legacy: ch["pending_return_echo"] -> ch["extra"]["status"]["pending_return_echo"]
        if "pending_return_echo" in ch and "pending_return_echo" not in st:
            st["pending_return_echo"] = bool(ch.get("pending_return_echo", False))
            try:
                del ch["pending_return_echo"]
            except Exception:
                ch["pending_return_echo"] = False
            changed = True

        # legacy: ch["sneaking"] -> ch["extra"]["status"]["sneaking"]
        if "sneaking" in ch and "sneaking" not in st:
            st["sneaking"] = bool(ch.get("sneaking", False))
            try:
                del ch["sneaking"]
            except Exception:
                ch["sneaking"] = False
            changed = True

        return changed

    def _room_characters(self, room_id: str) -> List[Dict[str, Any]]:
        """Return character records currently present in ``room_id``."""
        return self.bot.presence.get_players_in_room(room_id)

    def _room_members(self, room_id: str) -> List[Tuple[str, Dict[str, Any]]]:
        """Return ``(user_id, character)`` pairs currently present in ``room_id``."""
        return self.bot.presence.get_room_members(room_id)

    async def _broadcast_room(
        self,
        ctx: commands.Context,
        room_id: str,
        msg: str,
        *,
        exclude: Optional[Set[str]] = None,
    ) -> None:
        """Send msg to every player's run channel in the room (except excluded)."""
        exclude = exclude or set()
        for uid, ch in self._room_members(room_id):
            if uid in exclude:
                continue
            name = ch.get("name", "traveler")
            try:
                run_ch = await ensure_player_run_channel(self.bot, ctx, uid, name)
                if run_ch:
                    await run_ch.send(msg)
            except Exception:
                continue

    def _room_title(self, room_id: str) -> str:
        room = self.bot.storage.rooms.get(room_id, {})
        if isinstance(room, dict) and isinstance(room.get("title"), str) and room.get("title"):
            return room["title"]
        return room_id.replace("_", " ").title()

    # --------------------------------------------------
    # Look
    # --------------------------------------------------

    @commands.command()
    async def look(self, ctx: commands.Context):

        print(
            f"[LOOK ENTER] msg={ctx.message.id} "
            f"author={ctx.author} "
            f"channel={ctx.channel.name}"
        )

        s = self.bot.storage
        user_id = str(ctx.author.id)
        self.bot.state.ensure_player_records(user_id)

        ch = s.characters[user_id]
        changed = self._migrate_legacy_flags(ch)

        # Cube view
        if ch.get("in_cube"):
            cube = s.cubes.get(user_id, {})
            desc = (
                f"You stand in your {'own' if cube.get('owned') else 'shared'} Cube atrium. "
                f"Style: {cube.get('style','empty')}. Capacity: {cube.get('capacity',50)}."
            )
            items = cube.get("items", {})
            bag_txt = "— (empty)" if not items else ", ".join(f"{k} x{v}" for k, v in sorted(items.items()))
            embed = discord.Embed(title="Inside The Cube", description=desc)
            embed.add_field(name="Cube Items", value=bag_txt, inline=False)

            if changed:
                s.save_characters()

            await ctx.send(embed=embed)
            return

        # Entanglement guard: protect active thread nodes (ritual moments)
        if await _present_entanglement_if_any(self.bot, ctx, user_id):
            if changed:
                s.save_characters()
            return

        # VOID RESCUE
        room_before = ch.get("current_room")
        room_id = self.bot.state.resolve_room_for_user(user_id)
        if room_before != room_id:
            await ctx.send("🌀 Reality stitches itself back together. You’re pulled to safer ground…")

        room = s.rooms.get(room_id, {})
        if not isinstance(room, dict):
            room = {}

        title = self._room_title(room_id)
        desc = room.get("description", "") if isinstance(room.get("description"), str) else ""

        # Return Echo (contract-aligned status flag)
        status = self._status_get(ch)
        if room_id == "neptune_lounge" and bool(status.get("pending_return_echo", False)):
            echoes = room.get("return_echoes") or []
            if isinstance(echoes, list) and echoes:
                desc = f"{desc}\n\n{random.choice(echoes)}"
            self._status_set(ch, "pending_return_echo", False)
            changed = True

        content = desc.strip()

        # Enemies (room instances)
        enemies = room.get("enemies", {})
        if isinstance(enemies, dict) and enemies:
            lines = []
            for inst_id, en in enemies.items():
                hp = "?"
                if isinstance(en, dict):
                    hp = en.get("hp", "?")
                lines.append(f"👹 **{inst_id}** (HP: {hp})")
            if lines:
                content += "\n\n" + "\n".join(lines)

        # Items
        items_here = room.get("items", [])
        if isinstance(items_here, list) and items_here:
            content += f"\n\n👜 **Items here:** {', '.join(items_here)}"

        # Exits
        exits = room.get("exits", {})
        if isinstance(exits, dict) and exits:
            content += f"\n\n⇢ {', '.join(exits.keys())}"

        # Other players
        others = self.bot.presence.get_players_in_room(room_id, exclude_user_id=user_id)
        if others:
            content += "\n\n◉ PRESENCE\n"
            for oc in others:
                oc_name = oc.get("name", "Unknown")
                content += f"- {oc_name}\n"

        from fsbot.ui.console import room_embed, hud_embed

        embed = room_embed(
            title,
            content,
        )
        # --------------------------------------------------
        # TELEMETRY
        # --------------------------------------------------

        try:
            hud_cog = self.bot.get_cog("HudCog")

            if hud_cog:
                hud = hud_cog._get_hud(user_id)

                if hud:

                    if not hud.get("enabled", True):

                        telemetry_text = (
                            "SYSTEM OFFLINE\n"
                            "NO ACTIVE TELEMETRY"
                        )

                    elif hud.get("state") == "dark_mode":

                        telemetry_text = (
                            "SIGNAL LOST\n"
                            "..."
                        )

                    elif hud.get("state") == "signal_degraded":

                        telemetry_text = (
                            "♆ COHERENCE .......... ???\n"
                            "♄ PARALLELISM ........ ???\n"
                            f"✦ COMMOTION ........ {hud.get('commotion', 'LOW')}"
                        )

                    else:

                        telemetry_text = (
                            f"♆ COHERENCE .......... {hud.get('coherence', 97)}%\n"
                            f"♄ PARALLELISM ........ {hud.get('parallelism', 78)}%\n"
                            f"✦ COMMOTION ........ {hud.get('commotion', 'LOW')}"
                        )

        except Exception:
            pass

        if isinstance(room.get("image"), str) and room.get("image"):
            embed.set_image(url=room["image"])

        if changed:
            s.save_characters()

        if hud_cog and hud:

            hud_panel = hud_embed(
                coherence=hud.get("coherence", 97),
                parallelism=hud.get("parallelism", 78),
                commotion=hud.get("commotion", "LOW"),
            )
 
            await ctx.send(embed=embed)
            await ctx.send(embed=hud_panel)

        else:

            await ctx.send(embed=embed)

        # Optional room music
        if isinstance(room.get("soundcloud"), str) and room.get("soundcloud"):
            await self.bot.state.play_music(ctx, room["soundcloud"])

    # --------------------------------------------------
    # Movement (sneak suppression + thread node trigger)
    # --------------------------------------------------

    @commands.command(aliases=["move"])
    async def go(self, ctx: commands.Context, direction: str):
        s = self.bot.storage
        user_id = str(ctx.author.id)
        self.bot.state.ensure_player_records(user_id)

        ch = s.characters[user_id]
        changed = self._migrate_legacy_flags(ch)

        char_name = ch.get("name", ctx.author.display_name)

        if ch.get("in_cube"):
            if changed:
                s.save_characters()
            await ctx.send("You’re inside a Cube. Use `!cube_exit` to return to Triton Central.")
            return

        cur = self.bot.state.resolve_room_for_user(user_id)
        cur_room = s.rooms.get(cur, {})
        exits = cur_room.get("exits", {}) if isinstance(cur_room, dict) else {}

        direction = (direction or "").strip().lower()
        if not isinstance(exits, dict) or direction not in exits:
            if changed:
                s.save_characters()
            await ctx.send("You can’t go that way.")
            return

        new_room = exits[direction]

        sneaking = bool(self._status_get(ch).get("sneaking", False))

        # Departure echo (only if not sneaking)
        if not sneaking:
            await self._broadcast_room(
                ctx,
                cur,
                f"🚪 **{char_name}** leaves **{direction}**.",
                exclude={user_id},
            )

        # Move
        ch["current_room"] = new_room
        s.save_characters()  # movement is always a write

        # Event Model: fact is persisted before it is announced.
        await _publish_character_entered_room(
            self.bot,
            user_id=user_id,
            from_room_id=cur,
            to_room_id=new_room,
            movement_type="walk",
            direction=direction,
            sneaking=sneaking,
        )

        # Arrival echo (only if not sneaking)
        if not sneaking:
            await self._broadcast_room(
                ctx,
                new_room,
                f"🚪 **{char_name}** arrives.",
                exclude={user_id},
            )

        # Realm feed (global)
        if hasattr(self.bot, "send_to_realm_feed"):
            try:
                old_room_title = self._room_title(cur)
                new_room_title = self._room_title(new_room)
                await self.bot.send_to_realm_feed(
                    f"🚶 {char_name} moves from **{old_room_title}** to **{new_room_title}**."
                )
            except Exception:
                pass

        # If an on-enter thread node entangled the player, present it (and skip room render)
        if await _present_entanglement_if_any(self.bot, ctx, user_id):
            return

        await self.look(ctx)

    # --------------------------------------------------
    # DPC utilities
    # --------------------------------------------------

    @commands.command()
    async def rooms_find(self, ctx: commands.Context, *, term: str):
        if not is_dpc(ctx):
            await ctx.send("⛔ You don’t have permission to use `!rooms_find`.")
            return
        s = self.bot.storage
        term = term.lower().strip()
        matches = [rid for rid in s.rooms.keys() if term in rid.lower()][:30]
        if not matches:
            await ctx.send("No matching rooms.")
            return
        await ctx.send("🔎 Matches:\n" + "\n".join(f"`{m}`" for m in matches))

    @commands.command()
    async def teleport(self, ctx: commands.Context, *args):
        s = self.bot.storage

        # Allow DPCs OR characters who have explicitly unlocked teleport
        if not is_dpc(ctx):
            uid_self = str(ctx.author.id)
            self.bot.state.ensure_player_records(uid_self)
            ch_self = s.characters.get(uid_self, {})
            if not isinstance(ch_self, dict) or not _has_unlocked_command(ch_self, "teleport"):
                await ctx.send("⛔ You don’t have permission to use `!teleport`.")
                return

        if len(args) == 1:
            target_member = ctx.author
            room_id = args[0]
        elif len(args) == 2:
            if not ctx.message.mentions:
                await ctx.send("Usage: `!teleport @user <room_id>` or `!teleport <room_id>`")
                return
            target_member = ctx.message.mentions[0]
            room_id = args[1]
        else:
            await ctx.send("Usage: `!teleport <room_id>` or `!teleport @user <room_id>`")
            return

        room_id = room_id.strip().lower()
        if room_id not in s.rooms:
            suggestions = [rid for rid in s.rooms.keys() if room_id in rid][:12]
            hint = f"\nTry: " + ", ".join(f"`{sug}`" for sug in suggestions) if suggestions else ""
            await ctx.send(f"⚠️ Unknown room id `{room_id}`.{hint}")
            return

        uid = str(target_member.id)
        self.bot.state.ensure_player_records(uid)

        ch = s.characters[uid]
        self._migrate_legacy_flags(ch)
        previous_room = self.bot.state.resolve_room_for_user(uid)

        ch["in_cube"] = False
        ch["cube_context"] = None
        ch["current_room"] = room_id
        s.save_characters()

        # Event Model shadow publication: teleport is still a room-entry fact.
        await _publish_character_entered_room(
            self.bot,
            user_id=uid,
            from_room_id=previous_room,
            to_room_id=room_id,
            movement_type="teleport",
            direction=None,
            sneaking=False,
        )

        if target_member.id == ctx.author.id:
            await ctx.send(f"🌀 Teleported to **{self._room_title(room_id)}**.")
        else:
            await ctx.send(f"🌀 Teleported {target_member.mention} to **{self._room_title(room_id)}**.")

        # If teleport caused an entanglement moment, present it and stop.
        if await _present_entanglement_if_any(self.bot, ctx, uid):
            return

        # Otherwise render the room normally.
        await self.look(ctx)


async def setup(bot):
    await bot.add_cog(NavigationCog(bot))
