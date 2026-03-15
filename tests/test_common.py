import json
import os
import pathlib
import sys
import unittest

SRC_DIR = pathlib.Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import common


class CommonTests(unittest.TestCase):
    def test_validate_due_date_accepts_iso_datetime(self):
        self.assertTrue(common.validate_due_date("2026-03-20T12:00:00+05:30"))
        self.assertTrue(common.validate_due_date("2026-03-20T06:30:00Z"))

    def test_validate_due_date_rejects_invalid_value(self):
        self.assertFalse(common.validate_due_date("20-03-2026"))
        self.assertFalse(common.validate_due_date(""))

    def test_parse_limit_defaults_to_ten(self):
        limit, error = common.parse_limit({})
        self.assertEqual(limit, 10)
        self.assertIsNone(error)

    def test_parse_limit_rejects_large_values(self):
        limit, error = common.parse_limit({"limit": "100"})
        self.assertIsNone(limit)
        self.assertEqual(error["statusCode"], 400)

    def test_encode_decode_last_key_round_trip(self):
        original = {"taskId": "abc-123"}
        encoded = common.encode_last_key(original)
        decoded, error = common.decode_last_key(encoded)
        self.assertEqual(decoded, original)
        self.assertIsNone(error)

    def test_authorize_returns_401_when_token_is_required(self):
        previous = os.environ.get("API_TOKEN")
        os.environ["API_TOKEN"] = "secret"
        try:
            result = common.authorize({"headers": {}})
        finally:
            if previous is None:
                os.environ.pop("API_TOKEN", None)
            else:
                os.environ["API_TOKEN"] = previous

        self.assertEqual(result["statusCode"], 401)
        self.assertEqual(json.loads(result["body"])["message"], "Unauthorized")


if __name__ == "__main__":
    unittest.main()
