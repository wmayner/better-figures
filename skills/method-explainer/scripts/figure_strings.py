"""List every string in a rendered HTML figure, panel by panel, with word counts, for the spec's "Every string" section.

It reads the DOM after the page's scripts ran, so text that JavaScript writes (labels, numbers from the embedded data)
is included. A panel is a <section> element or any element with a data-panel attribute (give a band or divider between
steps its own data-panel, or its text is listed under the panel before it); text before the first panel is listed as
the top block (title, key). Run it after each render and paste the result into spec.md, so the spec's
strings stay those of the image. It flags every text block of more than 25 words for a look: quoted example content
and formulas are fine there, but an explanation in sentences belongs on the page.

    python3 -I figure_strings.py FIGURE.html          # dumps the DOM with a headless Chromium first
    python3 -I figure_strings.py --dom DOM.html       # or reads a DOM already dumped
"""
import glob
import html.parser
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKIP = {'script', 'style', 'title', 'head', 'defs', 'marker'}
LONG = 25  # a text block longer than this is a paragraph, which belongs on the page
BREAK = {'br', 'li', 'div', 'p', 'text', 'header', 'h1', 'h2', 'h3', 'h4', 'tr', 'figcaption'}


def find_browser():
    if os.environ.get('CHROME'):
        return os.environ['CHROME']
    roots = [os.environ.get('PLAYWRIGHT_BROWSERS_PATH', ''), os.path.expanduser('~/.cache/ms-playwright'),
             os.path.expanduser('~/Library/Caches/ms-playwright')]
    for root in filter(None, roots):
        hits = sorted(glob.glob(f'{root}/chromium_headless_shell-*/*/chrome-headless-shell'))
        if hits:
            return hits[-1]
    for name in ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', 'chromium', 'chromium-browser',
                 'google-chrome'):
        path = name if os.path.isabs(name) and os.access(name, os.X_OK) else shutil.which(name)
        if path:
            return path
    sys.exit('no headless browser: run "uvx playwright install chromium-headless-shell" or set CHROME')


def dump_dom(path):
    url = Path(path).resolve().as_uri()
    return subprocess.run([find_browser(), '--headless', '--dump-dom', '--allow-file-access-from-files',
                           '--virtual-time-budget=3000', url], capture_output=True, text=True, check=True).stdout


class Texts(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.panels, self.cur = [], [], None

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)
        a = dict(attrs)
        if tag == 'section' or 'data-panel' in a:
            self.cur = [f'@{a.get("data-panel") or a.get("id") or tag}\n']
            self.panels.append(self.cur)
        if self.cur is not None and tag in BREAK | {'span', 'tspan', 'td', 'th'}:
            self.cur.append('\n' if tag in BREAK else '' if tag == 'tspan' else ' | ')

    def handle_endtag(self, tag):
        while self.stack and self.stack.pop() != tag:
            pass

    def handle_data(self, data):
        if any(t in SKIP for t in self.stack):
            return
        if self.cur is None:
            self.cur = ['@top\n']
            self.panels.append(self.cur)
        self.cur.append(data)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    dom = Path(args[1]).read_text(encoding='utf-8') if args[0] == '--dom' else dump_dom(args[0])
    p = Texts()
    p.feed(dom)
    total, long = 0, []
    for panel in p.panels:
        name, *rest = ''.join(panel).split('\n')
        lines = [re.sub(r'\s+', ' ', x).strip() for x in rest]
        lines = [re.sub(r'^[|\s]+|[|\s]+$', '', re.sub(r'(\s*\|\s*)+', ' | ', x)) for x in lines]
        lines = [x for x in lines if x]
        if not lines:
            continue
        words = sum(len([w for w in x.split() if w != '|']) for x in lines)
        total += words
        print(f'--- {name[1:]} ({words} words)')
        for x in lines:
            n = len([w for w in x.split() if w != '|'])
            print('  ' + x + (f'   <-- {n} words' if n > LONG else ''))
            if n > LONG:
                long.append((name[1:], n, x[:70]))
    print('total words:', total)
    if long:
        print(f'\nPARAGRAPH CHECK: {len(long)} text blocks over {LONG} words. Look at each: quoted example content and '
              'formulas are fine, but a sentence that explains belongs on the page, with at most one short line left here:')
        for panel, n, start in long:
            print(f'  {panel}: {n} words: {start}...')


if __name__ == '__main__':
    main()
