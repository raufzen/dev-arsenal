import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import devbox

class TestDevBox(unittest.TestCase):
    def test_hash(self):
        res = devbox.cmd_hash("hello world")
        self.assertEqual(res["md5"], "5eb63bbbe01eeed093cb22bb8f5acdc3")
        self.assertEqual(res["sha256"], "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9")

    def test_base64_roundtrip(self):
        orig = "The quick brown fox jumps over the lazy dog"
        enc = devbox.cmd_base64(orig, decode=False)
        dec = devbox.cmd_base64(enc, decode=True)
        self.assertEqual(orig, dec)

    def test_json_formatter(self):
        valid_json = '{"b": 2, "a": 1}'
        formatted = devbox.cmd_json(valid_json)
        self.assertIsNotNone(formatted)
        self.assertIn('"a": 1', formatted)

    def test_uuid_generator(self):
        uuids = devbox.cmd_uuid(3)
        self.assertEqual(len(uuids), 3)
        for u in uuids:
            self.assertEqual(len(u), 36)

    def test_password_generator(self):
        pwd = devbox.cmd_password(24, symbols=True)
        self.assertEqual(len(pwd), 24)

    def test_timestamp(self):
        ts = devbox.cmd_timestamp("now")
        self.assertIsInstance(ts, int)
        self.assertGreater(ts, 1700000000)

    def test_jwt_inspection(self):
        token = "eyJhbGciOiAibm9uZSIgLCJ0eXAiOiAiSldUIn0.eyJzdWIiOiAiMTIzNDUiLCAibmFtZSI6ICJSYXVmIiwgImV4cCI6IDI1MDAwMDAwMDB9.signature"
        res = devbox.cmd_jwt(token)
        self.assertIsNotNone(res)
        self.assertEqual(res["payload"]["name"], "Rauf")

    def test_url_parser(self):
        res = devbox.cmd_url("https://example.com/api/test?user=rauf&debug=true")
        self.assertEqual(res["scheme"], "https")
        self.assertEqual(res["host"], "example.com")
        self.assertEqual(res["params"]["user"], ["rauf"])

    def test_regex_matcher(self):
        matches = devbox.cmd_regex(r"\d+", "port 8080 or 443")
        self.assertEqual(len(matches), 2)

    def test_color_converter(self):
        res = devbox.cmd_color("#FF5733")
        self.assertEqual(res["r"], 255)
        self.assertEqual(res["g"], 87)
        self.assertEqual(res["b"], 51)

if __name__ == "__main__":
    unittest.main()
