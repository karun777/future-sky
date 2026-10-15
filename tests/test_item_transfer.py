import unittest
from fsbot.item_transfer import transfer, TransferError


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.items = {"itm_lager": {"name": "Triton Lager"}}
        self.person = {"bag": {}}
        self.room = {"items": ["Triton Lager"]}

    def test_roundtrip(self):
        person, room, _ = transfer(self.person, self.room, self.items, "Triton Lager", "take")
        self.assertEqual(person["bag"]["itm_lager"], 1)
        self.assertEqual(room["items"], [])
        self.assertEqual(self.room["items"], ["Triton Lager"])
        person, room, _ = transfer(person, room, self.items, "itm_lager", "drop")
        self.assertEqual(person["bag"], {})
        self.assertEqual(room["items"], ["Triton Lager"])

    def test_cannot_take_missing(self):
        with self.assertRaises(TransferError):
            transfer(self.person, {"items": []}, self.items, "Triton Lager", "take")

    def test_cannot_drop_unowned(self):
        with self.assertRaises(TransferError):
            transfer(self.person, self.room, self.items, "Triton Lager", "drop")


if __name__ == "__main__":
    unittest.main()
