"""Cut a tall figure render into full-resolution pieces, for inspecting each region and for the fresh reader.

An image viewer (and the Read tool) shrinks a tall image to fit, so small text in a 2x render of a long figure
becomes unreadable. The pieces keep the render's own resolution and overlap a little, so nothing is lost at a cut.
Also writes whole.png, the full figure shrunk to at most 1600 px tall, for a look at the layout.

    uv run --with pillow python split_png.py FIGURE.png OUT_DIR [--height 2000] [--overlap 80] [--cols 1]
"""
import argparse
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('png')
    ap.add_argument('out_dir')
    ap.add_argument('--height', type=int, default=2000, help='piece height in the render\'s pixels')
    ap.add_argument('--overlap', type=int, default=80)
    ap.add_argument('--cols', type=int, default=1, help='also cut each band into this many columns')
    a = ap.parse_args()
    im = Image.open(a.png)
    w, h = im.size
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    whole = im.copy()
    whole.thumbnail((w, 1600))
    whole.save(out / 'whole.png')
    step = a.height - a.overlap
    tops = list(range(0, max(h - a.overlap, 1), step))
    n = 0
    for i, top in enumerate(tops):
        bottom = min(top + a.height, h)
        for j in range(a.cols):
            left, right = j * w // a.cols, (j + 1) * w // a.cols
            name = f'piece{i + 1:02d}' + (f'_{j + 1}' if a.cols > 1 else '') + '.png'
            im.crop((left, top, right, bottom)).save(out / name)
            n += 1
    print(f'{a.png}: {w} x {h} px -> {n} pieces and whole.png in {out}')


if __name__ == '__main__':
    main()
