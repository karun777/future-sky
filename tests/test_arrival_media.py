"""W6-F5 stage/media bindings with real arrival callbacks; fictional storage."""
import unittest
from copy import deepcopy
import test_arrival
from fsbot.cogs.arrival import ArrivalCog
from fsbot.arrival_media import BASE_URL, STAGES, pending_stage
from pathlib import Path
import hashlib, json

class ArrivalMediaTests(unittest.IsolatedAsyncioTestCase):
    setUp=test_arrival.ArrivalTests.setUp
    reload=test_arrival.ArrivalTests.reload
    act=test_arrival.ArrivalTests.act
    fill=test_arrival.ArrivalTests.fill
    def image(self):
        return self.ctx.messages[-1]["embed"].image.url
    async def test_preview_opens_inclination_without_mutation(self):
        before=deepcopy(self.storage.characters);disk=self.path.read_text()
        await self.act("preview")
        self.assertEqual(self.image(),BASE_URL+"inclination.webp")
        self.assertEqual(self.storage.characters,before);self.assertEqual(self.path.read_text(),disk)
    async def test_stage_transitions_use_all_five_media_in_order(self):
        await self.act("preview")
        images=[self.image()]
        await self.act("class Dreamer-Technician");images.append(self.image())
        await self.act("name Fiction");await self.act("date 2000-01-01");images.append(self.image())
        await self.act("body familiar");await self.act("embodiment unfamiliar");images.append(self.image())
        await self.act("review")
        self.assertEqual(self.image(),BASE_URL+"gathering.webp")
        await self.act("awaken")
        images.append(self.ctx.messages[-2]["embed"].image.url)
        self.assertEqual(images,[BASE_URL+s+".webp" for s in STAGES])
    async def test_review_uses_readable_class_and_keeps_body_choices(self):
        await self.fill(preview=True);await self.act("review")
        embed=self.ctx.messages[-1]["embed"]
        self.assertIn("Dreamer Technician",[f.value for f in embed.fields])
        self.assertEqual(embed.image.url,BASE_URL+"gathering.webp")
        self.assertIn("familiar",[f.value for f in embed.fields])
        self.assertIn("unfamiliar",[f.value for f in embed.fields])
    async def test_same_stage_edit_is_quiet_and_invalid_edit_never_advances(self):
        await self.act("preview");await self.act("class invalid")
        self.assertNotIn("embed",self.ctx.messages[-1])
        self.assertEqual(pending_stage(self.arrival.drafts[str(self.ctx.author.id)]),"inclination")
        await self.act("class Dreamer-Technician");await self.act("name Fiction")
        self.assertNotIn("embed",self.ctx.messages[-1])
        self.assertIn("date",self.ctx.text())
    async def test_help_and_cancel_do_not_capture_more_fields(self):
        await self.act("preview");before=deepcopy(self.arrival.drafts)
        await self.act("help")
        self.assertEqual(self.arrival.drafts,before)
        await self.act("cancel");self.assertFalse(self.arrival.drafts)
    def test_delivery_assets_match_manifest_and_are_valid_webp(self):
        root=Path(__file__).resolve().parents[1]/"assets/images/arrival/before_first_breath/v1"
        manifest=json.loads((root/"manifest.json").read_text())
        self.assertEqual(set(manifest["files"]),{s+".webp" for s in STAGES})
        for name,row in manifest["files"].items():
            data=(root/name).read_bytes()
            self.assertEqual(data[:4],b"RIFF")
            self.assertEqual(data[8:12],b"WEBP")
            self.assertEqual(len(data),row["bytes"])
            self.assertEqual(hashlib.sha256(data).hexdigest(),row["sha256"])
