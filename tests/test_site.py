"""Check the public page's install destinations and local resource links."""

from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = Page((ROOT / 'index.html').read_text(encoding='utf-8'))

    def test_install_links_use_expected_public_assets(self):
        links = [attrs['href'] for tag, attrs in self.page.tags
                 if tag == 'a' and attrs.get('href', '').startswith('codex:')]
        self.assertEqual(len(links), 2)
        found = set()
        for href in links:
            link = urlsplit(href)
            self.assertEqual((link.scheme, link.netloc, link.path), ('codex', 'pets', '/install'))
            self.assertFalse(link.fragment)
            params = parse_qs(link.query, strict_parsing=True)
            name = params['name'][0]
            folder = {'Woogi': 'woogi', 'Woogi Pixel': 'woogi-pixel'}[name]
            self.assertEqual(params, {
                'name': [name],
                'imageUrl': [f'https://raw.githubusercontent.com/phykn/woogi/main/pets/{folder}/spritesheet.png'],
                'spriteVersionNumber': ['2'],
            })
            self.assertTrue((ROOT / 'pets' / folder / 'spritesheet.png').is_file())
            found.add(folder)
        self.assertEqual(found, {'woogi', 'woogi-pixel'})

    def test_local_resources_and_fragment_targets_exist(self):
        ids = {attrs['id'] for _, attrs in self.page.tags if 'id' in attrs}
        self.assertTrue({'woogi', 'woogi-pixel'} <= ids)
        for tag, attrs in self.page.tags:
            if tag == 'img':
                self.assertTrue(attrs.get('alt'))
            for key in ('href', 'src'):
                if key not in attrs:
                    continue
                link = urlsplit(attrs[key])
                if link.scheme or link.netloc:
                    continue
                if link.path:
                    self.assertTrue((ROOT / link.path).is_file(), link.path)
                elif link.fragment:
                    self.assertIn(link.fragment, ids)


if __name__ == '__main__':
    unittest.main()
