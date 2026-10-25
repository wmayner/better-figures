// Shades each token by its score and draws the colour bar (see text.css). Load it at the end of <body>:
//   <script src="_kit/text.js"></script>
// Each .tokens element reads the JSON in the <script> right after it: [[token, score], ...], with null for a token
// that has no score. Scores below zero shade toward blue and scores above toward the accent, so tokens near zero
// stay white; text turns white on dark shades, and hovering a token shows its score. data-low and data-high set
// the ends of the scale (default: minus and plus the largest score in the figure). A token's leading space is
// drawn outside its shading, so words keep their gaps. The .scale element gets the colour bar, its ends and
// its data-label.
(function () {
  const css = getComputedStyle(document.documentElement);
  const accent = css.getPropertyValue("--accent").trim(), blue = css.getPropertyValue("--blue").trim();
  const rgb = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
  const mix = (a, b, t) => a.map((x, i) => Math.round(x + (b[i] - x) * Math.max(0, Math.min(1, t))));
  const lum = c => {
    const l = c.map(v => (v /= 255) <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
    return 0.2126 * l[0] + 0.7152 * l[1] + 0.0722 * l[2];
  };
  const fmt = v => (v < 0 ? "−" : v > 0 ? "+" : "") + Math.abs(v);
  const boxes = [...document.querySelectorAll(".tokens")];
  const rows = boxes.map(b => JSON.parse(b.nextElementSibling.textContent));
  const most = Math.max(...rows.flat().map(d => Math.abs(d[1] ?? 0)));
  let lo = -most, hi = most;
  boxes.forEach((box, k) => {
    lo = +(box.dataset.low ?? lo);
    hi = +(box.dataset.high ?? hi);
    const shade = v => v >= 0 ? mix([255, 255, 255], rgb(accent), v / hi) : mix([255, 255, 255], rgb(blue), v / lo);
    for (const [tok, v] of rows[k]) {
      const lead = tok.match(/^\s*/)[0];
      if (lead) box.appendChild(document.createTextNode(lead));
      const s = document.createElement("span");
      s.className = "t";
      s.textContent = tok.slice(lead.length);
      if (v != null) {
        const c = shade(v);
        s.style.background = `rgb(${c})`;
        if (lum(c) < 0.3) s.style.color = "#fff";
        s.title = v;
      }
      box.appendChild(s);
    }
  });
  document.querySelectorAll(".scale").forEach(sc => {
    sc.innerHTML = `<span>${sc.dataset.label || ""}</span><div><div class="bar" style="background:linear-gradient(to right,
      ${blue}, #fff, ${accent})"></div><div class="ends"><span>${fmt(lo)}</span><span>0</span><span>${fmt(hi)}</span>
      </div></div>`;
  });
})();
