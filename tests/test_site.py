"""Regression checks for the public project page and README entry points."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PublicSiteTests(unittest.TestCase):
    def test_page_has_share_metadata_and_clear_calls_to_action(self):
        page = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        for value in (
            'property="og:title"',
            'name="twitter:card"',
            'href="#quickstart"',
            '★ Star on GitHub',
            'data-copy=',
        ):
            self.assertIn(value, page)

    def test_page_references_existing_visual_assets(self):
        page = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        for asset in ("hero-screenshot.png", "architecture-diagram.svg"):
            self.assertIn(asset, page)
            self.assertTrue((ROOT / "docs" / "assets" / asset).is_file())

    def test_readme_links_to_the_walkthrough_and_guided_setup(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Explore the live walkthrough", readme)
        self.assertIn(".\\scripts\\setup.ps1", readme)
