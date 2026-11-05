"""W7-F8: private projections from fictional saved state, never live characters."""
from copy import deepcopy
from types import SimpleNamespace
import unittest
from fsbot.pod_opening import OPENING
from fsbot.hud_view import discovered_entries
from fsbot.cogs.hud import render_panel
from fsbot.web_character_view import character_view
import test_web_portal as portal_tests

def character(discoveries=()):
    return {"name": "Fictional", "current_room": "pod_room", "credits": 5,
            "bag": {}, "equipped": {}, "extra": {"arrival": {
                "opening": {"id": OPENING, "discoveries": list(discoveries)}}}}

def project(c):
    return character_view(SimpleNamespace(characters={"123": c}, rooms={}, items_db={}),
                          "123", allowed_discord_ids={"123"})

class HudProjectionTests(unittest.TestCase):
    def test_progression_does_not_reveal_undiscovered_booking(self):
        self.assertEqual(discovered_entries(character()), [])
        self.assertEqual([e["id"] for e in discovered_entries(character(["panels"]))], ["notice"])
        self.assertEqual([e["id"] for e in discovered_entries(character(["display"]))], ["feed7", "notice"])
        self.assertEqual([e["id"] for e in discovered_entries(character(["display", "booking"]))], ["feed7", "booking"])

    def test_absent_booking_and_unrelated_opening_do_not_grant_it(self):
        c = character(["display", "booking"])
        c["extra"]["arrival"]["performance_booking"] = False
        self.assertEqual([e["id"] for e in discovered_entries(c)], ["feed7"])
        c["extra"]["arrival"]["opening"]["id"] = "different-story"
        self.assertEqual(discovered_entries(c), [])

    def test_discord_and_web_share_known_entries_without_mutation(self):
        c = character(["display", "booking"]); before = deepcopy(c)
        web = project(c); discord = render_panel(c, explicit=True)
        self.assertEqual([(e["title"], e["text"]) for e in web["journal"]["entries"]],
                         [(f.name, f.value.split(" Open it")[0].split(" Revisit")[0]) for f in discord.fields])
        web["journal"]["entries"][0]["text"] = "Changed"
        self.assertEqual(c, before)

    def test_display_off_dimmed_and_degraded_preserve_memories(self):
        for enabled, state in [(False, "normal"), (True, "dark_mode"), (True, "signal_degraded")]:
            c = character(["booking"]); c["extra"]["hud"] = {"enabled": enabled, "state": state}
            view = project(c)
            self.assertEqual(view["display"], {"enabled": enabled, "state": state})
            self.assertEqual(view["journal"]["entries"][0]["id"], "booking")
            self.assertFalse(render_panel(c, explicit=True).fields)

    def test_sheet_exposes_only_saved_player_fields(self):
        c = character(); c.update(birthdate="2000-01-01",
            stats={"hp": 8, "max_hp": 12, "strength": 10, "secret": 999, "wisdom": True},
            pools={"fire": {"current": 2, "max": 4, "secret": "hidden"}, "secret": {"current": 99}})
        c["extra"]["profile"] = {"class_id": "maker", "admin_secret": "hidden"}
        sheet = project(c)["sheet"]
        self.assertEqual(sheet, {"birthdate": "2000-01-01", "class_id": "maker",
            "stats": {"hp": 8, "max_hp": 12, "strength": 10}, "pools": {"fire": {"current": 2, "max": 4}}})
        self.assertEqual(project(character())["sheet"]["stats"], {})

class HudHttpTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = portal_tests.WebPortalTests.asyncSetUp
    asyncTearDown = portal_tests.WebPortalTests.asyncTearDown
    start = portal_tests.WebPortalTests.start
    complete = portal_tests.WebPortalTests.complete
    sign_in = portal_tests.WebPortalTests.sign_in
    auth = portal_tests.WebPortalTests.auth

    async def test_authenticated_poll_tracks_saved_discovery_and_setting(self):
        token = await self.sign_in()
        self.bot.storage.characters["123"] = character()
        before = deepcopy(self.bot.storage.characters)
        response = await self.client.get("/play/api/me", headers=self.auth(token))
        self.assertEqual((await response.json())["journal"]["entries"], [])
        self.assertEqual(before, self.bot.storage.characters)
        c = character(["booking"]); c["extra"]["hud"] = {"enabled": False}
        self.bot.storage.characters["123"] = c
        response = await self.client.get("/play/api/me", headers=self.auth(token))
        view = await response.json()
        self.assertEqual(view["journal"]["entries"][0]["id"], "booking")
        self.assertFalse(view["display"]["enabled"])
        self.assertEqual(response.headers["Cache-Control"], "no-store")
