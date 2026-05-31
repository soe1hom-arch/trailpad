from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from trailpad import cli


class TrailpadTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        patcher = patch("trailpad.storage.APP_DIR", self.home / ".trailpad")
        self.addCleanup(patcher.stop)
        patcher.start()
        patcher2 = patch("trailpad.storage.STORE_FILE", (self.home / ".trailpad" / "vault.json"))
        self.addCleanup(patcher2.stop)
        patcher2.start()

    def run_cli(self, argv: list[str]) -> tuple[int, str]:
        out = []
        err = []

        def fake_print(*args, **kwargs):
            target = out if kwargs.get("file") is None else err
            target.append(" ".join(str(a) for a in args))

        with patch("builtins.print", side_effect=fake_print):
            code = cli.main(argv)
        return code, "\n".join(out + err)

    def test_init_add_list_and_export(self) -> None:
        code, _ = self.run_cli(["init"])
        self.assertEqual(code, 0)

        code, _ = self.run_cli(["add", "Ship", "release", "-t", "release"])
        self.assertEqual(code, 0)

        code, output = self.run_cli(["list"])
        self.assertEqual(code, 0)
        self.assertIn("Ship release", output)

        export_path = self.home / "export.md"
        code, _ = self.run_cli(["export", str(export_path)])
        self.assertEqual(code, 0)
        self.assertTrue(export_path.exists())
        self.assertIn("Trailpad Export", export_path.read_text())

    def test_pin_find_and_remove(self) -> None:
        self.run_cli(["init"])
        self.run_cli(["add", "Archive", "notes", "-t", "work"])
        self.run_cli(["pin", "1"])
        code, output = self.run_cli(["find", "work"])
        self.assertEqual(code, 0)
        self.assertIn("📌", output)
        self.run_cli(["rm", "1"])
        data = json.loads((self.home / ".trailpad" / "vault.json").read_text())
        self.assertEqual(data["notes"], [])


if __name__ == "__main__":
    unittest.main()

