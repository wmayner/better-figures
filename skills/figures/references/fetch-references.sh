#!/bin/sh
# Download the summary figures listed in README.md from arXiv, for personal reference.
# These papers are under arXiv's default license, which does not allow redistribution, so the images are not
# in this repository. The script saves each paper's PDF and renders the page that holds its Figure 1 to
# fetched/<name>_page<N>.png next to this script. Needs curl, and pdftoppm (poppler) or gs (Ghostscript).
#   sh fetch-references.sh
set -e
here=$(cd "$(dirname "$0")" && pwd)
out="$here/fetched"
mkdir -p "$out"
dpi=150

render() {  # render <pdf> <page> <png>
  if command -v pdftoppm >/dev/null 2>&1; then
    pdftoppm -png -r "$dpi" -f "$2" -l "$2" -singlefile "$1" "${3%.png}"
  elif command -v gs >/dev/null 2>&1; then
    gs -q -dNOPAUSE -dBATCH -sDEVICE=png16m -r"$dpi" -dFirstPage="$2" -dLastPage="$2" -sOutputFile="$3" "$1"
  else
    echo "need pdftoppm (poppler) or gs (Ghostscript) to render PDF pages" >&2; exit 1
  fi
}

# name arXiv-id-and-version page-with-Figure-1
while read -r name id page; do
  [ -n "$name" ] || continue
  pdf="$out/$name.pdf"; png="$out/${name}_page$page.png"
  [ -s "$pdf" ] || curl -sSfL -o "$pdf" "https://arxiv.org/pdf/$id"
  render "$pdf" "$page" "$png"
  echo "wrote $png"
done <<'LIST'
connecting-the-dots 2406.14546v3 2
reversal-curse 2309.12288v4 1
subliminal-learning 2507.14805v1 1
emergent-misalignment 2502.17424v7 1
tell-me-about-yourself 2501.11120v1 2
LIST
