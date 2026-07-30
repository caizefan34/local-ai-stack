from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ShortcutInstallerTests(unittest.TestCase):
    def test_icon_and_installer_are_present(self):
        self.assertTrue((ROOT / "desktop-app" / "assets" / "nailong-mascot.ico").is_file())
        installer = (ROOT / "desktop-app" / "install-shortcut.ps1").read_text(encoding="utf-8")
        self.assertIn("WScript.Shell", installer)
        self.assertIn("nailong-mascot.ico", installer)
        self.assertIn("Start Local AI Stack.cmd", installer)


if __name__ == "__main__":
    unittest.main()
