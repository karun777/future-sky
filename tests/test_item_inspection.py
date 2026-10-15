import unittest
from fsbot.item_inspection import inspect_item


class InspectionTests(unittest.TestCase):
    def setUp(self):
        self.items = {"itm_book": {"name": "Tiny Book", "attributes": {"size": "tiny"},
                      "discoveries": {"clue": {"attributes": {"purpose": "gift"}}}}}
        self.room = {"items": ["Tiny Book"]}
        self.person = {"bag": {}, "equipped": {}, "item_discoveries": {}}

    def test_ground_visible(self):
        _, _, attrs, _ = inspect_item("tiny book", self.person, self.room, self.items)
        self.assertEqual(attrs, {"size": "tiny"})

    def test_hidden_discovery(self):
        self.person["item_discoveries"] = {"itm_book": ["clue"]}
        _, _, attrs, _ = inspect_item("Tiny Book", self.person, self.room, self.items)
        self.assertEqual(attrs["purpose"], "gift")

    def test_not_visible(self):
        with self.assertRaises(ValueError):
            inspect_item("Tiny Book", self.person, {"items": []}, self.items)

    def test_bag_visible(self):
        self.person["bag"]["itm_book"] = 1
        self.assertEqual(inspect_item("Tiny Book", self.person, {"items": []}, self.items)[0], "itm_book")


if __name__ == "__main__":
    unittest.main()
