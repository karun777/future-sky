import unittest
from fsbot.token_exchange import TOKEN, ExchangeError, discover_token, exchange_token


class TokenExchangeTests(unittest.TestCase):
    def test_discover_and_exchange(self):
        original = {"current_room": "pod_room", "bag": {}}
        found = discover_token(original)
        self.assertEqual(original["bag"], {})
        self.assertEqual(found["bag"][TOKEN], 1)
        with self.assertRaises(ExchangeError):
            discover_token(found)
        found["current_room"] = "neptune_lounge"
        exchanged = exchange_token(found)
        self.assertNotIn(TOKEN, exchanged["bag"])
        self.assertTrue(exchanged["flags"]["counterkeeper_token_received"])
        self.assertEqual(found["bag"][TOKEN], 1)
        with self.assertRaises(ExchangeError):
            exchange_token(exchanged)

    def test_location_and_possession(self):
        with self.assertRaises(ExchangeError):
            discover_token({"current_room": "neptune_lounge"})
        with self.assertRaises(ExchangeError):
            exchange_token({"current_room": "neptune_lounge", "bag": {}})
        with self.assertRaises(ExchangeError):
            exchange_token({"current_room": "pod_room", "bag": {TOKEN: 1}})


if __name__ == "__main__":
    unittest.main()
