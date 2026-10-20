#!/bin/sh
# Render an HTML figure or diagram to PNG at 2x: render_html.sh in.html out.png [width] [height]
# width and height are the .canvas or .fig size in CSS pixels (default 1600 x 700).
# Browser, first found: $CHROME; Playwright's headless shell (in $PLAYWRIGHT_BROWSERS_PATH or the
# default Linux or macOS cache); Google Chrome; chromium; google-chrome.
# Install the headless shell with: uvx playwright install chromium-headless-shell
#                              or: npx playwright install chromium-headless-shell
set -e
[ -f "$1" ] || { echo "usage: render_html.sh in.html out.png [width] [height]" >&2; exit 2; }
in=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
mkdir -p "$(dirname "$2")"
out=$(cd "$(dirname "$2")" && pwd)/$(basename "$2")
w=${3:-1600}; h=${4:-700}
browser=${CHROME:-}
if [ -z "$browser" ]; then
  for root in "${PLAYWRIGHT_BROWSERS_PATH:-}" "$HOME/.cache/ms-playwright" "$HOME/Library/Caches/ms-playwright"; do
    [ -n "$root" ] && [ -d "$root" ] || continue
    browser=$(ls -d "$root"/chromium_headless_shell-*/*/chrome-headless-shell 2>/dev/null | tail -1)
    [ -n "$browser" ] && break
  done
fi
if [ -z "$browser" ]; then
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" "$(command -v chromium || true)" \
           "$(command -v chromium-browser || true)" "$(command -v google-chrome || true)"; do
    [ -n "$c" ] && [ -x "$c" ] && browser=$c && break
  done
fi
[ -n "$browser" ] || { echo "no headless browser: run 'uvx playwright install chromium-headless-shell' or set CHROME" >&2; exit 1; }
"$browser" --headless --screenshot="$out" --window-size="$w,$h" --force-device-scale-factor=2 --hide-scrollbars \
  --allow-file-access-from-files --default-background-color=FFFFFFFF --virtual-time-budget=3000 "file://$in" 2>/dev/null
echo "wrote $out"
