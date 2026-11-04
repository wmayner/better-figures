"""Render a tall HTML figure at its own height, cut it into pieces, and check its layout.

One command for the loop of step 6: it lays the figure out in a headless Chromium, measures the figure element's
height, renders it at 2x with the figures skill's render_html.sh at exactly that height (so nothing is cut off and
there is no blank tail), cuts the render into full-resolution pieces (split_png.py) and one crop per panel, and reports:
  - each panel's top and height in CSS px (a <section> or an element with data-panel);
  - every element that runs past the figure's right edge;
  - every text element under 12 px, other than sub- and superscripts.

    uv run --with pillow python render_check.py FIGURE.html OUT_DIR [--width 1200] [--figure '#figure']

The figure element is the first of --figure, .canvas, .fig, body. The figures skill's render_html.sh is found in
$FIGURES_SKILL_DIR, or else as the newest copy in the plugin cache.
"""
import argparse
import glob
import html
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_strings import find_browser  # noqa: E402

PROBE = """<script>document.fonts.ready.then(() => {
  const sel = %s;
  const fig = sel.map(s => document.querySelector(s)).find(Boolean) || document.body;
  const F = fig.getBoundingClientRect(), out = [];
  let bottom = F.bottom;
  for (const e of fig.querySelectorAll('*')) { const r = e.getBoundingClientRect(); if (r.height) bottom = Math.max(bottom, r.bottom); }
  out.push('HEIGHT ' + Math.ceil(bottom + Math.max(F.top, 0) + window.scrollY));
  for (const e of document.querySelectorAll('section, [data-panel]')) {
    const r = e.getBoundingClientRect();
    out.push('PANEL ' + (e.dataset.panel || e.id || e.tagName.toLowerCase()) + ' ' + Math.round(r.top - F.top) + ' ' + Math.round(r.height));
  }
  for (const e of fig.querySelectorAll('*')) {
    const r = e.getBoundingClientRect();
    if (!r.width) continue;
    const text = (e.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 50);
    if (r.right > F.right + 0.5) out.push('OVERFLOW ' + Math.round(r.right - F.right) + 'px ' + e.tagName.toLowerCase() + ': ' + text);
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    const fs = parseFloat(getComputedStyle(e).fontSize);
    if (own && fs < 12 && !e.closest('sub, sup')) out.push('SMALL ' + fs + 'px: ' + text);
  }
  document.body.setAttribute('data-render-check', out.join('\\n'));
});</script>"""


def measure(fig_html, out_dir, width, selectors):
    src = fig_html.read_text(encoding='utf-8')
    base = f'<base href="{fig_html.parent.resolve().as_uri()}/">'
    src = re.sub(r'<head[^>]*>', lambda m: m.group(0) + base, src, count=1) if '<head' in src else base + src
    probe = PROBE % ('[' + ', '.join(repr(s) for s in selectors) + ']')
    src = src.replace('</body>', probe + '</body>', 1) if '</body>' in src else src + probe
    tmp = out_dir / '.render_check_probe.html'
    tmp.write_text(src, encoding='utf-8')
    try:
        dom = subprocess.run([find_browser(), '--headless', '--dump-dom', '--allow-file-access-from-files',
                              '--virtual-time-budget=3000', f'--window-size={width},3000', tmp.as_uri()],
                             capture_output=True, text=True, check=True).stdout
    finally:
        tmp.unlink()
    m = re.search(r'data-render-check="([^"]*)"', dom)
    if not m:
        sys.exit('the probe did not run: does the page load its fonts and scripts from files beside it?')
    return html.unescape(m.group(1)).splitlines()


def render_script():
    if os.environ.get('FIGURES_SKILL_DIR'):
        return Path(os.environ['FIGURES_SKILL_DIR']) / 'render_html.sh'
    beside = Path(__file__).resolve().parents[2] / 'figures' / 'render_html.sh'  # the figures skill in the same plugin
    if beside.is_file():
        return beside
    hits = glob.glob(os.path.expanduser('~/.claude*/plugins/cache/better-figures/better-figures/*/skills/figures/render_html.sh'))
    key = lambda p: [int(x) if x.isdigit() else 0 for x in Path(p).parts[-4].split('.')]
    if not hits:
        sys.exit('render_html.sh not found: set FIGURES_SKILL_DIR to the figures skill\'s directory')
    return Path(max(hits, key=key))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('figure')
    ap.add_argument('out_dir')
    ap.add_argument('--width', type=int, default=1200)
    ap.add_argument('--figure', dest='selector', default='#figure')
    a = ap.parse_args()
    fig, out = Path(a.figure).resolve(), Path(a.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    lines = measure(fig, out, a.width, [a.selector, '.canvas', '.fig'])
    height = int(lines[0].split()[1])
    png = out / (fig.stem + '.png')
    subprocess.run(['sh', str(render_script()), str(fig), str(png), str(a.width), str(height)], check=True)
    subprocess.run([sys.executable, str(Path(__file__).resolve().parent / 'split_png.py'), str(png), str(out / 'pieces')],
                   check=True)
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    im, crops = Image.open(png), out / 'panels'
    crops.mkdir(exist_ok=True)
    for l in lines:
        if l.startswith('PANEL '):
            name, top, h = l.split()[1:4]
            box = (0, max(0, 2 * int(top) - 12), im.width, min(im.height, 2 * (int(top) + int(h)) + 12))
            im.crop(box).save(crops / f'{re.sub(r"[^A-Za-z0-9_-]", "_", name)}.png')
    print(f'figure: {a.width} x {height} CSS px; one crop per panel in {crops}')
    for kind in ('PANEL', 'OVERFLOW', 'SMALL'):
        found = [l[len(kind) + 1:] for l in lines if l.startswith(kind + ' ')]
        print(f'{kind.lower()}: {len(found)}' + ('' if kind == 'PANEL' or not found else '  <-- fix'))
        for l in found[:40]:
            print('  ' + l)


if __name__ == '__main__':
    main()
