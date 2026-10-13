"""Check generated output and source assets without changing tracked previews."""

from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw

from scripts import preview


ROOT = Path(__file__).resolve().parents[1]
DURATIONS = [180] * 10 + [140] * 5 + [100] * 8


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = patch.object(preview, 'ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def source_path(self, folder):
        path = self.root / 'pets' / folder / 'spritesheet.png'
        path.parent.mkdir(parents=True)
        return path

    def check_gif(self, path):
        with Image.open(path) as gif:
            self.assertEqual(gif.format, 'GIF')
            self.assertEqual(gif.size, (192, 208))
            self.assertEqual(gif.n_frames, 23)
            self.assertEqual(gif.info['loop'], 0)
            for index, duration in enumerate(DURATIONS):
                gif.seek(index)
                self.assertEqual(gif.info['duration'], duration)

    def test_selection_order_timing_and_alpha_compositing(self):
        sheet = Image.new('RGBA', (1536, 2288))
        draw = ImageDraw.Draw(sheet)
        for row in range(11):
            for col in range(8):
                draw.rectangle(
                    (col * 192, row * 208, (col + 1) * 192 - 1, (row + 1) * 208 - 1),
                    fill=(row * 21, col * 29, 80, 128),
                )
        sheet.save(self.source_path('sample'))
        preview.build('sample')
        path = self.root / 'previews/sample.gif'
        self.check_gif(path)
        positions = [(row, col) for row, count in ((0, 6), (3, 4), (4, 5), (1, 8)) for col in range(count)]
        with Image.open(path) as gif:
            for index, (row, col) in enumerate(positions):
                gif.seek(index)
                pixel = gif.convert('RGB').getpixel((96, 104))
                expected = tuple(round((value * 128 + bg * 127) / 255)
                                 for value, bg in zip((row * 21, col * 29, 80), (238, 242, 247)))
                self.assertEqual(pixel, expected)
            gif.seek(0)
            with Image.open(path.with_suffix('.png')) as still:
                self.assertEqual(still.convert('RGB').tobytes(), gif.convert('RGB').tobytes())

    def test_wrong_dimensions_rejected_before_decode(self):
        Image.new('RGBA', (1535, 2288)).save(self.source_path('wrong'))
        with patch.object(Image.Image, 'convert', side_effect=AssertionError('decoded invalid sheet')):
            with self.assertRaisesRegex(ValueError, '1536 x 2288'):
                preview.build('wrong')
        self.assertFalse((self.root / 'previews').exists())

    def test_corrupt_input_has_no_partial_output(self):
        self.source_path('broken').write_bytes(b'not a PNG')
        with self.assertRaises(OSError):
            preview.build('broken')
        self.assertFalse((self.root / 'previews').exists())

    def test_published_assets_rebuild_without_changes(self):
        for folder in ('woogi', 'woogi-pixel'):
            with self.subTest(folder=folder):
                source = ROOT / 'pets' / folder / 'spritesheet.png'
                with Image.open(source) as sheet:
                    self.assertEqual((sheet.format, sheet.mode, sheet.size), ('PNG', 'RGBA', (1536, 2288)))
                    self.assertEqual(sheet.getchannel('A').getextrema(), (0, 255))
                shutil.copyfile(source, self.source_path(folder))
                preview.build(folder)
                for ext in ('gif', 'png'):
                    path = Path('previews') / f'{folder}.{ext}'
                    self.assertEqual((self.root / path).read_bytes(), (ROOT / path).read_bytes())
                self.check_gif(self.root / 'previews' / f'{folder}.gif')


if __name__ == '__main__':
    unittest.main()
