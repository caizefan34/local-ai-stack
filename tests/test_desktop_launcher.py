from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DesktopLauncherTests(unittest.TestCase):
    def test_launcher_starts_control_plane_and_has_browser_fallback(self):
        launcher = (ROOT / "desktop-app" / "launch.ps1").read_text(encoding="utf-8")
        self.assertIn("control_plane", launcher)
        self.assertIn("--app=$url", launcher)
        self.assertIn("Start-Process $url", launcher)
        self.assertIn("127.0.0.1", launcher)


if __name__ == "__main__":
    unittest.main()
