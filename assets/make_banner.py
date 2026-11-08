"""Usage: python assets/make_banner.py FONT_DIR OUT.svg  (FONT_DIR holds Outfit.ttf and Fraunces.ttf from github.com/google/fonts, SIL OFL).
Animated banner for VikVador/Talks: title on the left, a small slide deck flipping through four slides on the right.
Text is drawn as paths (Outfit, SIL OFL) and maths with matplotlib mathtext, so the SVG needs no font."""

import math
import random
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path
from matplotlib.textpath import TextPath

FONT_DIR, OUT = sys.argv[1], sys.argv[2]
# Title font: family, weight, extra axes, size, tracking (chosen with the comparison sheet)
import json
import os

TITLE = json.loads(os.environ.get("TITLE", '{"family": "Fraunces", "weight": 600, "axes": {"SOFT": 100, "WONK": 1, "opsz": 144}, "size": 150, "tracking": 0.0}'))
W, H = 1280, 320
T = 16.0  # seconds for the whole loop, 4 slides of 4 s

NAVY, BLUE, CORAL, TEXT = "#1d3557", "#457b9d", "#e07a5f", "#2a2f3a"
BG0, BG1 = "#060a17", "#0b1430"
INK0, INK1, SUB = "#f4f6ff", "#b9c6ee", "#b4c0e2"

_fonts = {}


def font(weight, family="Outfit", axes=None):
    key = (family, weight, tuple(sorted((axes or {}).items())))
    if key not in _fonts:
        f = TTFont(f"{FONT_DIR}/{family}.ttf")
        if "fvar" in f:
            loc = {"wght": weight, **(axes or {})}
            loc = {a.axisTag: loc.get(a.axisTag, a.defaultValue) for a in f["fvar"].axes}
            f = instancer.instantiateVariableFont(f, loc)
        _fonts[key] = f
    return _fonts[key]


def text(s, x, y, size, weight=400, tracking=0.0, anchor="start", family="Outfit", axes=None):
    """Path data for a string, baseline at y. Returns (d, width)."""
    f = font(weight, family, axes)
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    k = size / f["head"].unitsPerEm
    width = sum(hmtx[cmap[ord(c)]][0] * k + tracking * size for c in s) - tracking * size
    x0 = x - width if anchor == "end" else x - width / 2 if anchor == "middle" else x
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}")
    cx = x0
    for c in s:
        g = cmap[ord(c)]
        gs[g].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
        cx += hmtx[g][0] * k + tracking * size
    return pen.getCommands(), width


def tex(s, x, y, size):
    """Path data for mathtext, baseline at y. Returns (d, width)."""
    tp = TextPath((0, 0), s, size=size, prop=FontProperties(family="serif", math_fontfamily="cm"))
    ext = tp.get_extents()
    parts, i = [], 0
    for verts, code in tp.iter_segments():
        pts = [(x + verts[j] - ext.x0, y - verts[j + 1]) for j in range(0, len(verts), 2)]
        cmd = {Path.MOVETO: "M", Path.LINETO: "L", Path.CURVE3: "Q", Path.CURVE4: "C", Path.CLOSEPOLY: "Z"}[code]
        parts.append(cmd + ("" if code == Path.CLOSEPOLY else " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)))
        i += 1
    return " ".join(parts), ext.width


def pct(t):
    return f"{100 * t / T:.3f}%"


def keyframes(name, frames):
    """frames: list of (time in s, css declarations)."""
    return f"@keyframes {name} {{ " + " ".join(f"{pct(t)} {{ {css} }}" for t, css in frames) + " }"


css, defs, body = [], [], []

# ---------- background: night gradient, faint grid, twinkling stars ----------
defs.append(f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>')
defs.append(f'<linearGradient id="ink" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK0}"/><stop offset="1" stop-color="{INK1}"/></linearGradient>')
body.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
for gx in range(0, W + 1, 64):
    body.append(f'<path d="M{gx},0 V{H}" stroke="#2a3866" stroke-opacity=".18"/>')
for gy in range(0, H + 1, 64):
    body.append(f'<path d="M0,{gy} H{W}" stroke="#2a3866" stroke-opacity=".18"/>')
rng = random.Random(7)
css.append(".star { animation: twinkle 4s ease-in-out infinite alternate; } @keyframes twinkle { from { opacity: .12; } }")
for _ in range(70):
    sx, sy = rng.uniform(0, W), rng.uniform(0, H)
    if 700 < sx < 1230 and 20 < sy < 300:
        continue
    body.append(f'<circle class="star" cx="{sx:.0f}" cy="{sy:.0f}" r="{rng.uniform(.5, 1.3):.1f}" fill="#fff" '
                f'opacity="{rng.uniform(.3, .8):.2f}" style="animation-delay:-{rng.uniform(0, 4):.1f}s"/>')

# ---------- left: title and subtitle ----------
d, _ = text("TALKS", 60, 212, TITLE["size"], weight=TITLE["weight"], tracking=TITLE["tracking"], family=TITLE["family"], axes=TITLE["axes"])
body.append(f'<path d="{d}" fill="url(#ink)"/>')

# ---------- right: a deck of slides ----------
SX, SY, SW, SH = 770, 34, 420, 236
k = SW / 1280  # template slide (1280 x 720) -> card
for off, col in [(16, "#1b2850"), (8, "#24346a")]:
    body.append(f'<rect x="{SX + off}" y="{SY - off}" width="{SW}" height="{SH}" rx="6" fill="{col}" opacity=".9"/>')
defs.append('<filter id="shadow" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000" flood-opacity=".45"/></filter>')
defs.append(f'<clipPath id="card"><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="6"/></clipPath>')
body.append(f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="6" fill="#fff" filter="url(#shadow)"/>')

N, D, TR = 4, T / 4, 0.45  # slides, seconds per slide, transition


def slide_anim(i):
    a, b = i * D, (i + 1) * D
    if i == 0:
        frames = [(0, "opacity:1; transform:none"), (b - TR, "opacity:1; transform:none"),
                  (b, "opacity:0; transform:translateX(-24px)"), (T - TR, "opacity:0; transform:translateX(24px)"),
                  (T, "opacity:1; transform:none")]
    else:
        frames = [(0, "opacity:0; transform:translateX(24px)"), (a - TR, "opacity:0; transform:translateX(24px)"),
                  (a, "opacity:1; transform:none"), (b - TR, "opacity:1; transform:none"),
                  (b, "opacity:0; transform:translateX(-24px)"), (T, "opacity:0; transform:translateX(-24px)")]
        if i == N - 1:
            frames = frames[:4] + [(T, "opacity:0; transform:translateX(-24px)")]
    css.append(f".s{i} {{ animation: s{i} {T}s ease-in-out infinite; }} " + keyframes(f"s{i}", frames))


def appear(name, t0, t1, end, extra_from="", extra_to=""):
    """Element hidden until t0, shown from t1 to end, hidden after (times in s)."""
    css.append(f".{name} {{ animation: {name} {T}s ease-out infinite; }} " + keyframes(name, [
        (0, f"opacity:0; {extra_from}"), (t0, f"opacity:0; {extra_from}"), (t1, f"opacity:1; {extra_to}"),
        (end, f"opacity:1; {extra_to}"), (min(end + TR, T), f"opacity:0; {extra_to}"), (T, f"opacity:0; {extra_from}")]))


def page(i):
    d, _ = text(f"{i + 1} / {N}", SX + SW - 14, SY + SH - 10, 9, weight=400, anchor="end")
    col = "#b9cdf5" if i == 3 else "#9aa3b5"
    return f'<path d="{d}" fill="{col}"/>'


slides = []

# Slide 1: the title slide (white panel, thesis title, pixelated ocean on the right)
g = [f'<g class="s0" clip-path="url(#card)">', f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" fill="#fff"/>']
rng = random.Random(3)
stops = ["#0d1b3d", "#2f5d8a", "#8fb8de", "#f6e3c8", "#f2a65a", "#c8553d", "#5a1e1e"]


def cmap(v):
    """Diverging ocean colours, v in [0, 1]."""
    v = min(max(v, 0), 1) * (len(stops) - 1)
    i = min(int(v), len(stops) - 2)
    a, b = stops[i], stops[i + 1]
    m = v - i
    return "#" + "".join(f"{round(int(a[j:j + 2], 16) * (1 - m) + int(b[j:j + 2], 16) * m):02x}" for j in (1, 3, 5))


def field(u, w):
    """A smooth field with a few eddies, like a sea surface temperature anomaly."""
    v = 0.5 + 0.22 * math.sin(3.1 * u + 1.3 * w) + 0.16 * math.sin(5.3 * w - 2.0 * u + 1)
    for ex, ey, s, r in [(0.75, 0.3, 0.35, 0.12), (0.45, 0.7, -0.3, 0.15), (0.9, 0.85, 0.25, 0.1)]:
        v += s * math.exp(-((u - ex) ** 2 + (w - ey) ** 2) / r ** 2)
    return v


px = 14
x_cut = lambda y: SX + 255 - (y - SY) * 0.26  # diagonal edge of the picture, like the template
for gy in range(SY, SY + SH, px):
    for gx in range(int(x_cut(gy + px)) - px, SX + SW, px):
        u, w = (gx - SX) / SW, (gy - SY) / SH
        col = cmap(field(u, w) + rng.uniform(-0.04, 0.04))
        delay = 0.2 + 1.4 * (gx - SX - 160) / (SW - 160) + rng.uniform(0, 0.25)  # a satellite pass, left to right
        g.append(f'<rect class="pxl" x="{gx}" y="{gy}" width="{px}" height="{px}" fill="{col}" style="animation-delay:{delay:.2f}s"/>')
g.append(f'<path d="M{SX},{SY} H{x_cut(SY):.1f} L{x_cut(SY + SH):.1f},{SY + SH} H{SX} Z" fill="#fff"/>')
g.append(f'<path d="M{x_cut(SY):.1f},{SY} L{x_cut(SY + SH):.1f},{SY + SH}" stroke="{NAVY}" stroke-width="3"/>')
for j, line in enumerate(["Understanding the Ocean", "from Observations Using", "Deep Learning"]):
    d, _ = text(line, SX + 26, SY + 52 + 27 * j, 17, weight=700)
    g.append(f'<path d="{d}" fill="{NAVY}"/>')
g.append(f'<rect x="{SX + 26}" y="{SY + 140}" width="1.5" height="26" fill="{NAVY}"/>')
d, _ = text("PRESENTED BY", SX + 32, SY + 148, 6.5, weight=600, tracking=0.12)
g.append(f'<path d="{d}" fill="{NAVY}"/>')
d, _ = text("Victor Mangeleer", SX + 32, SY + 162, 10, weight=500)
g.append(f'<path d="{d}" fill="{BLUE}"/>')
g.append("</g>")
css.append(".pxl { animation: pxl " + f"{T}s linear infinite; }} " + keyframes("pxl", [(0, "opacity:.0"), (0.6, "opacity:1"), (T, "opacity:1")]))
slide_anim(0)
slides.append("".join(g))

# Slide 2: maths, Bayes' rule with its three terms named one after the other
g = [f'<g class="s1" clip-path="url(#card)">', f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" fill="#fff"/>']
d, _ = text("Reconstruction from space", SX + 100 * k, SY + 180 * k + 10, 15, weight=700)
g.append(f'<path d="{d}" fill="{NAVY}"/>')
d, _ = text("We want the posterior over the ocean state given the observations,", SX + 100 * k, SY + 92, 9, weight=300)
g.append(f'<path d="{d}" fill="{TEXT}"/>')
terms = [r"$p(x \mid y)$", r"$\propto$", r"$p(y \mid x)$", r"$p(x)$"]
names = ["posterior", None, "likelihood", "prior"]
sizes = [tex(t, 0, 0, 26)[1] for t in terms]
gap = 12
cx = SX + (SW - (sum(sizes) + gap * (len(terms) - 1))) / 2
base = SY + 150
for j, (t, w, nm) in enumerate(zip(terms, sizes, names)):
    d, _ = tex(t, cx, base, 26)
    g.append(f'<path d="{d}" fill="{BLUE}"/>')
    if nm:
        n = f"t{j}"
        t0 = D + 0.8 + 0.7 * [0, 0, 1, 2][j]
        appear(n, t0, t0 + 0.35, 2 * D - TR, "transform:translateY(4px)", "transform:none")
        g.append(f'<g class="{n}"><rect x="{cx:.1f}" y="{base + 12}" width="{w:.1f}" height="2" fill="{CORAL}"/>')
        dd, _ = text(nm, cx + w / 2, base + 30, 10, weight=400, anchor="middle")
        g.append(f'<path d="{dd}" fill="{CORAL}"/></g>')
    cx += w + gap
g.append(page(1) + "</g>")
slide_anim(1)
slides.append("".join(g))

# Slide 3: a result, an ensemble drawn over time, a key-result box
g = [f'<g class="s2" clip-path="url(#card)">', f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" fill="#fff"/>']
ax0, ay0, aw, ah = SX + 40, SY + 30, 200, 112
g.append(f'<path d="M{ax0},{ay0} V{ay0 + ah} H{ax0 + aw}" fill="none" stroke="#9aa3b5" stroke-width="1"/>')
import math

def curve(phase, amp, rise):
    pts = []
    for s in range(0, 41):
        u = s / 40
        yv = 0.15 + rise * u + amp * math.sin(6 * u + phase) * (0.3 + u)
        pts.append((ax0 + 6 + u * (aw - 12), ay0 + ah - 8 - yv * (ah - 20)))
    return "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)

rng = random.Random(11)
for m in range(6):
    g.append(f'<path class="ens" d="{curve(rng.uniform(-.5, .5), rng.uniform(.05, .12), .55 + rng.uniform(-.08, .08))}" '
             f'fill="none" stroke="{BLUE}" stroke-opacity=".35" stroke-width="1" pathLength="100"/>')
g.append(f'<path class="mean" d="{curve(0, .08, .55)}" fill="none" stroke="{NAVY}" stroke-width="2" pathLength="100"/>')
for cls, t0, t1 in [("ens", 2 * D + 0.4, 2 * D + 2.0), ("mean", 2 * D + 0.9, 2 * D + 2.4)]:
    css.append(f".{cls} {{ stroke-dasharray: 100 100; animation: {cls} {T}s ease-in-out infinite; }} " + keyframes(cls, [
        (0, "stroke-dashoffset:100"), (t0, "stroke-dashoffset:100"), (t1, "stroke-dashoffset:0"), (T, "stroke-dashoffset:0")]))
d, _ = text("lead time", ax0 + aw, ay0 + ah + 12, 8, weight=300, anchor="end")
g.append(f'<path d="{d}" fill="#9aa3b5"/>')
tx = ax0 + aw + 24
for j, (w, bold) in enumerate([(130, True), (110, False), (120, False), (70, False)]):
    g.append(f'<rect x="{tx}" y="{ay0 + 34 + 13 * j}" width="{w}" height="5" rx="2.5" fill="{NAVY if bold else "#c9cfdb"}"/>')
g.append(f'<rect class="key" x="{SX + 32}" y="{SY + 168}" width="{SW - 64}" height="34" fill="#eef3f8"/>'
         f'<rect class="key" x="{SX + 32}" y="{SY + 168}" width="3" height="34" fill="{BLUE}"/>')
d, _ = text("Key result.", SX + 46, SY + 189, 10, weight=700)
g.append(f'<path class="key" d="{d}" fill="{NAVY}"/><rect class="key" x="{SX + 108}" y="{SY + 183}" width="190" height="5" rx="2.5" fill="#c9cfdb"/>')
appear("key", 2 * D + 2.4, 2 * D + 2.8, 3 * D - TR)
g.append(page(2) + "</g>")
slide_anim(2)
slides.append("".join(g))

# Slide 4: dark "What's next" slide, bullets appearing one by one
g = [f'<g class="s3" clip-path="url(#card)">', f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" fill="{NAVY}"/>']
d, _ = text("What's next", SX + 100 * k, SY + 180 * k + 10, 15, weight=700)
g.append(f'<path d="{d}" fill="#fff"/>')
for j, w in enumerate([210, 170, 230]):
    n = f"b{j}"
    t0 = 3 * D + 0.6 + 0.55 * j
    appear(n, t0, t0 + 0.35, T - TR, "transform:translateX(-6px)", "transform:none")
    y = SY + 112 + 24 * j
    g.append(f'<g class="{n}"><circle cx="{SX + 38}" cy="{y}" r="2.5" fill="#b9cdf5"/>'
             f'<rect x="{SX + 50}" y="{y - 3}" width="{w}" height="6" rx="3" fill="#fff" opacity=".85"/></g>')
g.append(page(3) + "</g>")
slide_anim(3)
slides.append("".join(g))
body.extend(slides)

# ---------- under the deck: progress dots ----------
for i in range(N):
    cx = SX + SW / 2 + (i - 1.5) * 18
    body.append(f'<circle cx="{cx}" cy="{SY + SH + 24}" r="3" fill="#3a4a7a"/>')
    a = i * D
    frames = [(0, "opacity:0"), (max(a - .01, 0), "opacity:0"), (a + .01, "opacity:1"), (a + D, "opacity:1"),
              (min(a + D + .01, T), "opacity:0"), (T, "opacity:0")]
    if i == 0:
        frames = [(0, "opacity:1"), (D, "opacity:1"), (D + .01, "opacity:0"), (T, "opacity:0")]
    css.append(f".d{i} {{ animation: d{i} {T}s step-end infinite; }} " + keyframes(f"d{i}", frames))
    body.append(f'<circle class="d{i}" cx="{cx}" cy="{SY + SH + 24}" r="3.5" fill="{CORAL}"/>')

css.append("@media (prefers-reduced-motion: reduce) { * { animation: none !important; } .s1, .s2, .s3 { opacity: 0; } }")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
       f'<style>{" ".join(css)}</style><defs>{"".join(defs)}</defs>{"".join(body)}</svg>')
open(OUT, "w").write(svg)
print(f"{OUT}: {len(svg) / 1024:.0f} KB")
