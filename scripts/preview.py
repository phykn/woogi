"""Build looping README GIFs from the original v2 sprite sheets (Pillow required)."""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CELL = (192, 208)
# Idle, greet, jump, and walk right. Timings are illustrative preview timings.
SEQUENCE = [(0, 6, 180), (3, 4, 180), (4, 5, 140), (1, 8, 100)]


def build(folder):
    sheet = Image.open(ROOT / 'pets' / folder / 'spritesheet.png').convert('RGBA')
    if sheet.size != (1536, 2288):
        raise ValueError(f'{folder}: expected a 1536 x 2288 v2 sprite sheet')
    frames, durations = [], []
    for row, count, duration in SEQUENCE:
        for col in range(count):
            x, y = col * CELL[0], row * CELL[1]
            frame = sheet.crop((x, y, x + CELL[0], y + CELL[1]))
            canvas = Image.new('RGBA', CELL, '#eef2f7')
            canvas.alpha_composite(frame)
            frames.append(canvas.convert('RGB').quantize(colors=256))
            durations.append(duration)
    output = ROOT / 'previews' / f'{folder}.gif'
    output.parent.mkdir(exist_ok=True)
    frames[0].save(output, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, disposal=2, optimize=False)
    print(f'{output.name}: {len(frames)} frames')


if __name__ == '__main__':
    for folder in ('woogi', 'woogi-pixel'):
        build(folder)
