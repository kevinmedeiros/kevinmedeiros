#!/usr/bin/env python3
"""Build the AS-BUILT GitHub profile: engineering-drawing SVG plates + README.md.

    python3 scripts/gen_profile.py

Inputs : profile.config.json, assets/profile.json, assets/fonts/*.woff2
Outputs: assets/stage/*.svg and README.md (generated, do not hand-edit)
Art direction: direcao.md

GitHub renders SVGs as <img>: CSS animation runs, links inside do not. Every
clickable thing (project, revision, stamp) is its own SVG wrapped in <a>.
Each piece paints its own navy plate; anything drawn outside a plate uses a
mid-tone that reads on GitHub light and dark. Content is complete at t=0 and
prefers-reduced-motion switches motion off. If fontTools is installed the
embedded fonts are subset per SVG; otherwise the Latin subsets are embedded.
"""
from __future__ import annotations

import base64
import glob
import html
import io
import json
import math
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "profile.config.json")))
DATA_PATH = os.path.join(ROOT, "assets", "profile.json")
DATA = json.load(open(DATA_PATH)) if os.path.exists(DATA_PATH) else {}
OUT_DIR = os.path.join(ROOT, "assets", "stage")
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
REL = "assets/stage"
W = 900

NAVY, LINE, DIM, GOLD, RULE = "#0c1626", "#d7e6f5", "#8ea6c0", "#e6c98a", "#6f8aa8"
EASE = "cubic-bezier(.16,1,.3,1)"
FONTS = {  # css family -> (file, weight, style)
    "PlexCond": [("plex-cond-700.woff2", 700, "normal"), ("plex-cond-500.woff2", 500, "normal"),
                 ("plex-cond-400i.woff2", 400, "italic")],
    "PlexMono": [("plex-mono-500.woff2", 500, "normal")],
}
COND = "PlexCond,'IBM Plex Sans Condensed','Arial Narrow',sans-serif"
MONO = "PlexMono,'IBM Plex Mono',Menlo,Consolas,monospace"

try:  # optional: per-SVG subsetting + exact text measurement
    from fontTools import subset as _subset
    from fontTools.ttLib import TTFont as _TTFont
except Exception:  # pragma: no cover
    _subset = _TTFont = None


def esc(s):
    return html.escape(str(s), quote=True)


def fmt(n):
    return f"{int(n):,}"


# ------------------------------------------------------------------ fonts
_ADV = {}


def _advances(fname):
    if fname not in _ADV:
        if _TTFont is None:
            _ADV[fname] = None
        else:
            f = _TTFont(os.path.join(FONT_DIR, fname))
            cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
            _ADV[fname] = ({cp: hmtx[g][0] / upm for cp, g in cmap.items()}, 0.5)
    return _ADV[fname]


def text_w(s, size, fname="plex-cond-500.woff2", spacing=0.0):
    a = _advances(fname)
    if a is None:
        per = 0.6 if "mono" in fname else 0.47
        return len(s) * size * per + spacing * len(s)
    table, dflt = a
    return sum(table.get(ord(c), dflt) for c in s) * size + spacing * len(s)


def wrap(s, size, max_w, fname="plex-cond-500.woff2"):
    lines, cur = [], ""
    for word in s.split():
        t = (cur + " " + word).strip()
        if cur and text_w(t, size, fname) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = t
    return lines + ([cur] if cur else [])


def font_css(text):
    chars = set(text) | set(" 0123456789")
    out = []
    for fam, faces in FONTS.items():
        for fname, weight, style in faces:
            path = os.path.join(FONT_DIR, fname)
            if not os.path.exists(path):
                continue
            data = open(path, "rb").read()
            if _subset is not None:
                try:
                    f = _TTFont(path)
                    o = _subset.Options()
                    o.flavor = "woff2"
                    o.layout_features = ["kern", "liga", "tnum", "lnum"]
                    s = _subset.Subsetter(o)
                    s.populate(text="".join(sorted(chars)))
                    s.subset(f)
                    b = io.BytesIO()
                    f.flavor = "woff2"
                    f.save(b)
                    data = b.getvalue()
                except Exception:
                    pass
            out.append(f"@font-face{{font-family:{fam};font-weight:{weight};font-style:{style};"
                       f"src:url(data:font/woff2;base64,{base64.b64encode(data).decode()}) format('woff2')}}")
    return "".join(out)


BASE_CSS = f"""
text{{font-kerning:normal}}
.plot{{stroke-dasharray:var(--l);stroke-dashoffset:var(--l);animation:plot 1.9s {EASE} forwards,fadeout .8s ease-out 2.4s forwards}}
@keyframes plot{{to{{stroke-dashoffset:0}}}}
@keyframes fadeout{{to{{opacity:0}}}}
.sweep{{animation:sweep 2.2s {EASE} .15s both}}
@keyframes sweep{{0%{{transform:translateX(0);opacity:1}}85%{{opacity:1}}100%{{transform:translateX(var(--d));opacity:0}}}}
.pulse{{animation:pulse 3.2s cubic-bezier(.45,0,.55,1) 1.6s infinite both}}
@keyframes pulse{{0%{{transform:translateY(0);opacity:0}}8%{{opacity:1}}88%{{opacity:1}}100%{{transform:translateY(var(--h));opacity:0}}}}
.recon{{animation:recon 3.2s ease-out 1.6s infinite}}
@keyframes recon{{0%,38%{{fill-opacity:0}}46%{{fill-opacity:.85}}100%{{fill-opacity:0}}}}
.breathe{{animation:breathe 2.8s ease-in-out infinite}}
@keyframes breathe{{50%{{opacity:.15}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.plot,.sweep,.pulse{{display:none}}}}
"""

TEXTS = []  # all strings drawn in the current piece (for subsetting)


def T(s):
    TEXTS.append(str(s))
    return esc(s)


def svg(w, h, title, body, defs="", css=""):
    fonts = font_css("".join(TEXTS) + title)
    TEXTS.clear()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(title)}">'
            f"<title>{esc(title)}</title><style>{fonts}{BASE_CSS}{css}</style><defs>{defs}</defs>{body}</svg>\n")


def paper_defs(uid):
    return (f'<pattern id="{uid}g1" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M10 0H0V10" fill="none" stroke="{LINE}" stroke-opacity=".045"/></pattern>'
            f'<pattern id="{uid}g2" width="50" height="50" patternUnits="userSpaceOnUse"><path d="M50 0H0V50" fill="none" stroke="{LINE}" stroke-opacity=".085"/></pattern>'
            f'<filter id="{uid}gr" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7"/>'
            f'<feColorMatrix values="0 0 0 0 .84  0 0 0 0 .9  0 0 0 0 .96  0 0 0 .07 0"/><feComposite in2="SourceGraphic" operator="in"/></filter>'
            f'<marker id="{uid}ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1L10 5L0 9" fill="none" stroke="{DIM}" stroke-width="1.4"/></marker>'
            f'<marker id="{uid}ag" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="{GOLD}"/></marker>')


def paper(uid, shape):
    """Navy plate with grid + grain, clipped to `shape` (an SVG element string)."""
    return (f'<clipPath id="{uid}c">{shape}</clipPath><g clip-path="url(#{uid}c)">'
            f'<rect width="100%" height="100%" fill="{NAVY}"/><rect width="100%" height="100%" fill="url(#{uid}g1)"/>'
            f'<rect width="100%" height="100%" fill="url(#{uid}g2)"/><rect width="100%" height="100%" fill="#fff" filter="url(#{uid}gr)"/></g>')


def write(name, content):
    with open(os.path.join(OUT_DIR, name), "w") as f:
        f.write(content)
    return f"{REL}/{name}"


def balloon(x, y, label, r=10, size=10, stroke=LINE, fill=NAVY, color=LINE):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}"/>'
            f'<text x="{x:.1f}" y="{y + size * .36:.1f}" font-family="{MONO}" font-weight="500" font-size="{size}" fill="{color}" text-anchor="middle">{T(label)}</text>')


# ------------------------------------------------------------------ data
def name_parts():
    parts = CFG["name"].upper().split()
    return parts[0], " ".join(parts[1:])


def record():
    bits = []
    if DATA.get("commits"):
        bits.append(f"{fmt(DATA['commits'])} COMMITS")
    if DATA.get("repos"):
        bits.append(f"{DATA['repos']} REPOS")
    m = re.search(r"(\d+\+?) years", CFG.get("intro", ""))
    if m:
        bits.append(f"{m.group(1)} YRS")
    return "  ·  ".join(bits)


def rev_date():
    u = DATA.get("updated", "")
    return u[:7].replace("-", ".") if u else ""


def general_note():
    about = CFG.get("about", [])
    return " ".join(a for a in about if a.strip() != CFG.get("founded", "").strip())


BOM_ORDER = ["Cloud", "Containers", "Observability", "CI/CD & GitOps", "Automation & IaC", "Languages", "Data"]


def bom_rows():
    by = {s["area"]: s["items"] for s in CFG.get("stack", [])}
    order = [a for a in BOM_ORDER if a in by] + [a for a in by if a not in BOM_ORDER]
    return [(a, by[a]) for a in order]


def founded_names():
    f = CFG.get("founded", "")
    return [p["label"] for p in CFG.get("projects", []) if p["label"] in f]


# ------------------------------------------------------------------ hero (sheet 01)
C30, S30 = math.cos(math.radians(30)), 0.5


def iso(x, y, z, cx=650, cy=236, s=0.78):
    return (cx + (x - y) * C30 * s, cy + (x + y) * S30 * s - z * s)


def P(pts):
    return " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)


def perim(pts, closed=True):
    n = len(pts)
    return sum(math.dist(pts[i], pts[(i + 1) % n]) for i in range(n if closed else n - 1))


def build_hero():
    H = 452
    u = "h"
    first, last = name_parts()
    b, plot = [paper(u, f'<rect width="{W}" height="{H}" rx="10"/>')], []
    # frame + zone markers
    b.append(f'<rect x="14" y="14" width="{W-28}" height="{H-28}" fill="none" stroke="{LINE}" stroke-opacity=".55"/>'
             f'<rect x="22" y="22" width="{W-44}" height="{H-44}" fill="none" stroke="{LINE}" stroke-opacity=".22"/>')
    for i in range(1, 9):
        x = 22 + i * (W - 44) / 9
        b.append(f'<path d="M{x:.0f} 14V22M{x:.0f} {H-22}V{H-14}" stroke="{LINE}" stroke-opacity=".5"/>')
    for i in range(9):
        x = 22 + (i + .5) * (W - 44) / 9
        b.append(f'<text x="{x:.0f}" y="20.5" font-family="{MONO}" font-size="7" fill="{DIM}" text-anchor="middle">{T(i + 1)}</text>')
    for i, L in enumerate("ABCD"):
        y = 22 + (i + .5) * (H - 44) / 4
        b.append(f'<path d="M14 {22 + (i+1)*(H-44)/4:.0f}H22M{W-22} {22 + (i+1)*(H-44)/4:.0f}H{W-14}" stroke="{LINE}" stroke-opacity=".5"/>'
                 f'<text x="18" y="{y+2.5:.0f}" font-family="{MONO}" font-size="7" fill="{DIM}" text-anchor="middle">{T(L)}</text>')

    # identity: role as a dimension over the surname
    nx, fs = 50, 98
    wl = text_w(last, fs, "plex-cond-700.woff2", -1)
    x0, x1 = nx + 3, nx + wl - 2
    role = CFG["role"].upper()
    rw = text_w(role, 10, "plex-mono-500.woff2", 1.5) + 18
    b.append(f'<g stroke="{DIM}" fill="none"><path d="M{x0:.0f} 78V90M{x1:.0f} 78V90"/>'
             f'<path d="M{x0+4:.0f} 84H{x1-4:.0f}" marker-start="url(#{u}ar)" marker-end="url(#{u}ar)"/></g>'
             f'<rect x="{(x0+x1)/2 - rw/2:.0f}" y="77" width="{rw:.0f}" height="14" fill="{NAVY}"/>'
             f'<text x="{(x0+x1)/2:.0f}" y="87.5" font-family="{MONO}" font-weight="500" font-size="10" fill="{LINE}" text-anchor="middle" letter-spacing="1.5">{T(role)}</text>')
    b.append(f'<text x="{nx}" y="172" font-family="{COND}" font-weight="700" font-size="{fs}" fill="{LINE}" letter-spacing="-1">{T(first)}</text>'
             f'<text x="{nx}" y="256" font-family="{COND}" font-weight="700" font-size="{fs}" fill="none" stroke="{LINE}" stroke-width="1.6" letter-spacing="-1">{T(last)}</text>')
    b.append(f'<text x="{nx+3}" y="300" font-family="{COND}" font-style="italic" font-weight="400" font-size="24" fill="{LINE}">'
             f'{T(CFG["tagline_lead"])} <tspan fill="{GOLD}" font-weight="700" font-style="normal">{T(CFG["tagline_accent"])}</tspan>{T(CFG["tagline_rest"])}</text>')
    # legend (explains the loop)
    ly = 384
    b.append(f'<text x="{nx+3}" y="{ly-22}" font-family="{MONO}" font-weight="500" font-size="8" fill="{DIM}" letter-spacing="1.5">{T("LEGEND")}</text>'
             f'<path d="M{nx+3} {ly-14}H{nx+230}" stroke="{DIM}" stroke-opacity=".5"/>'
             f'<path d="M{nx+3} {ly}H{nx+33}" stroke="{GOLD}" stroke-width="1.3" stroke-dasharray="4 3"/><circle cx="{nx+18}" cy="{ly}" r="3" fill="{GOLD}"/>'
             f'<text x="{nx+42}" y="{ly+3.5}" font-family="{MONO}" font-size="9" fill="{LINE}" letter-spacing=".6">{T("GITOPS SYNC PATH, GIT TO ARGO CD")}</text>'
             f'<rect x="{nx+10}" y="{ly+14}" width="12" height="12" fill="{GOLD}" fill-opacity=".2" stroke="{GOLD}"/>'
             f'<text x="{nx+42}" y="{ly+24}" font-family="{MONO}" font-size="9" fill="{LINE}" letter-spacing=".6">{T("POD RECONCILED ON EACH SYNC")}</text>')

    # exploded axonometric
    S, TH = 80, 10
    layers = [(0, "1", "CLOUD · AWS / GCP"), (82, "2", "CLUSTER · KUBERNETES"), (164, "3", "OBSERVE")]

    def slab(z):
        top = [iso(-S, -S, z), iso(S, -S, z), iso(S, S, z), iso(-S, S, z)]
        front = [iso(S, -S, z), iso(S, S, z), iso(S, S, z - TH), iso(S, -S, z - TH)]
        left = [iso(-S, S, z), iso(S, S, z), iso(S, S, z - TH), iso(-S, S, z - TH)]
        out = ""
        for poly, op in ((left, .10), (front, .05), (top, 0)):
            out += f'<polygon points="{P(poly)}" fill="{LINE}" fill-opacity="{op}" stroke="{LINE}" stroke-width="1.2" stroke-linejoin="round"/>'
            plot.append((poly, True))
        return out

    def cube(x, y, z, a, gold=False):
        t = [iso(x, y, z + a), iso(x + a, y, z + a), iso(x + a, y + a, z + a), iso(x, y + a, z + a)]
        f = [iso(x + a, y, z + a), iso(x + a, y + a, z + a), iso(x + a, y + a, z), iso(x + a, y, z)]
        l = [iso(x, y + a, z + a), iso(x + a, y + a, z + a), iso(x + a, y + a, z), iso(x, y + a, z)]
        col = GOLD if gold else LINE
        top_fill = f'<polygon points="{P(t)}" fill="{NAVY}"/>'
        if gold:
            top_fill += f'<polygon class="recon" points="{P(t)}" fill="{GOLD}" fill-opacity="0"/>'
        return (f'<g stroke="{col}" stroke-width="1" stroke-linejoin="round"><polygon points="{P(l)}" fill="{col}" fill-opacity=".22"/>'
                f'<polygon points="{P(f)}" fill="{col}" fill-opacity=".1"/>{top_fill}<polygon points="{P(t)}" fill="none"/></g>')

    g = [slab(0)]
    # cloud slab: two regions (AWS / GCP) as a dashed partition
    pa, pb = iso(0, -S, 0), iso(0, S, 0)
    g.append(f'<path d="M{pa[0]:.1f} {pa[1]:.1f}L{pb[0]:.1f} {pb[1]:.1f}" stroke="{LINE}" stroke-opacity=".5" stroke-dasharray="3 4"/>')
    g.append(slab(82))
    for i in range(3):
        for j in range(3):
            if (i, j) == (1, 1):
                continue
            g.append(cube(-60 + i * 44, -60 + j * 44, 82, 22, gold=(i, j) == (2, 0)))
    g.append(slab(164))
    # observe slab: three probe targets (measurement points)
    for (px, py) in ((-44, -40), (30, -10), (-10, 40)):
        c = iso(px, py, 164)
        g.append(f'<g stroke="{LINE}" fill="none" stroke-width="1"><ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="9" ry="5.2"/>'
                 f'<path d="M{c[0]-13:.1f} {c[1]:.1f}h26M{c[0]:.1f} {c[1]-7:.1f}v14"/></g>')
    # GitOps sync path
    a0, a1 = iso(0, 0, -106), iso(0, 0, 252)
    g.append(f'<path d="M{a0[0]:.1f} {a0[1]:.1f}V{a1[1]:.1f}" stroke="{GOLD}" stroke-width="1.3" stroke-dasharray="4 4" marker-end="url(#{u}ag)"/>')
    g.append(f'<circle cx="{a0[0]:.1f}" cy="{a0[1]:.1f}" r="3.5" fill="none" stroke="{GOLD}" stroke-width="1.3"/>')
    g.append(f'<text x="{a0[0]+10:.1f}" y="{a0[1]+4:.1f}" font-family="{MONO}" font-weight="500" font-size="9" fill="{GOLD}" letter-spacing="1.2">{T("GIT")}</text>'
             f'<text x="{a1[0]-12:.1f}" y="{a1[1]+7:.1f}" font-family="{MONO}" font-weight="500" font-size="9" fill="{GOLD}" text-anchor="end" letter-spacing="1.2">{T("ARGO CD SYNC")}</text>')
    g.append(f'<g transform="translate({a0[0]:.1f},{a0[1]:.1f})"><circle class="pulse" style="--h:{a1[1]-a0[1]+8:.0f}px" r="3.8" fill="{GOLD}"/></g>')
    # balloons -> BOM items
    for z, num, lab in layers:
        x0_, y0_ = iso(S, -S, z - TH / 2)
        bx = 866
        g.append(f'<path d="M{x0_:.1f} {y0_:.1f}H{bx-11}" stroke="{DIM}" stroke-dasharray="1 3"/><circle cx="{x0_:.1f}" cy="{y0_:.1f}" r="2" fill="{DIM}"/>'
                 + balloon(bx, y0_, num) +
                 f'<text x="{bx-16}" y="{y0_-6:.1f}" font-family="{MONO}" font-weight="500" font-size="7.5" fill="{DIM}" text-anchor="end" letter-spacing="1">{T(lab)}</text>')
    b.append("".join(g))

    # title block
    tx, ty, tw, th = 548, 340, 330, 90
    rows = [("TITLE", "GENERAL ARRANGEMENT", "SHEET", "01 / 05"),
            ("DRAWN", CFG["name"].upper(), "REV.", rev_date()),
            ("LOC.", CFG["location"].upper(), None, None),
            ("RECORD", record(), None, None)]
    tb = [f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="{NAVY}" stroke="{LINE}" stroke-opacity=".7"/>']
    for i in range(1, 4):
        tb.append(f'<path d="M{tx} {ty + i*22.5:.1f}H{tx+tw}" stroke="{LINE}" stroke-opacity=".3"/>')
    tb.append(f'<path d="M{tx+52} {ty}V{ty+th}M{tx+238} {ty}V{ty+45}M{tx+276} {ty}V{ty+45}" stroke="{LINE}" stroke-opacity=".3"/>')
    for i, (k1, v1, k2, v2) in enumerate(rows):
        y = ty + 15 + i * 22.5
        big = i == 0
        tb.append(f'<text x="{tx+8}" y="{y}" font-family="{MONO}" font-size="7.5" fill="{DIM}" letter-spacing="1">{T(k1)}</text>'
                  f'<text x="{tx+60}" y="{y + (1 if big else 0)}" font-family="{COND if big else MONO}" font-weight="{700 if big else 500}" font-size="{13 if big else 9}" fill="{GOLD if big else LINE}" letter-spacing="{.6 if big else .4}">{T(v1)}</text>')
        if k2:
            tb.append(f'<text x="{tx+244}" y="{y}" font-family="{MONO}" font-size="7.5" fill="{DIM}" letter-spacing="1">{T(k2)}</text>'
                      f'<text x="{tx+284}" y="{y}" font-family="{MONO}" font-weight="500" font-size="9" fill="{LINE}">{T(v2)}</text>')
    b.append("".join(tb))

    # plotter pass (entrance): gold pen retraces the axonometric, crosshair sweeps
    pp = []
    for k, (poly, closed) in enumerate(plot):
        L = perim(poly, closed)
        pp.append(f'<polygon class="plot" style="--l:{L:.0f};animation-delay:{.1 + k*.06:.2f}s,{2.4 + k*.02:.2f}s" points="{P(poly)}" fill="none" stroke="{GOLD}" stroke-width="1.6" stroke-linejoin="round"/>')
    b.append("".join(pp))
    b.append(f'<g class="sweep" style="--d:{W-60}px"><path d="M30 26V{H-26}" stroke="{GOLD}" stroke-opacity=".55"/>'
             f'<path d="M22 {H/2}h16" stroke="{GOLD}"/><circle cx="30" cy="{H/2}" r="5" fill="none" stroke="{GOLD}"/></g>')
    alt = (f"{CFG['name']}, {CFG['role']}. {CFG['tagline_lead']} {CFG['tagline_accent']}{CFG['tagline_rest']} "
           f"{CFG['location']}. {record().title()}.")
    return write("hero.svg", svg(W, H, alt, "".join(b), paper_defs(u))), alt


# ------------------------------------------------------------------ section tab
def build_tab(fname, sheet, title):
    H = 88
    u = "t" + str(sheet)
    tw = max(380, text_w(title, 34, "plex-cond-700.woff2") + 190)
    shape = f'<path d="M0 14H{tw-18}L{tw} 32V78H0Z"/>'
    b = [paper(u, shape), f'<path d="M0.5 14.5H{tw-18}L{tw-.5} 32V77.5H.5Z" fill="none" stroke="{LINE}" stroke-opacity=".5"/>']
    b.append(f'<text x="26" y="60" font-family="{COND}" font-weight="700" font-size="34" fill="{LINE}" letter-spacing="-.4">{T(title)}</text>')
    sx = tw - 104
    b.append(f'<path d="M{sx} 26V70" stroke="{LINE}" stroke-opacity=".35"/>'
             f'<text x="{sx+14}" y="40" font-family="{MONO}" font-size="7.5" fill="{DIM}" letter-spacing="1">{T("SHEET")}</text>'
             f'<text x="{sx+14}" y="62" font-family="{COND}" font-weight="700" font-size="20" fill="{GOLD}">{T(f"{sheet:02d} / 05")}</text>')
    # scale bar in RULE (reads on light and dark)
    x0, x1, y = tw + 30, W - 12, 52
    n = 8
    seg = (x1 - x0) / n
    for i in range(n):
        fill = RULE if i % 2 == 0 else "none"
        b.append(f'<rect x="{x0 + i*seg:.1f}" y="{y-4}" width="{seg:.1f}" height="8" fill="{fill}" stroke="{RULE}"/>')
    for i in range(n + 1):
        h_ = 9 if i % 4 == 0 else 5
        b.append(f'<path d="M{x0 + i*seg:.1f} {y+4}v{h_}" stroke="{RULE}"/>')
    return write(fname, svg(W, H, title, "".join(b), paper_defs(u)))


# ------------------------------------------------------------------ sheet 02: BOM + general note
def build_bom():
    rows = bom_rows()
    rh, top = 33, 66
    H = top + rh * len(rows) + 34
    u = "b"
    b = [paper(u, f'<rect width="{W}" height="{H}" rx="4"/>'),
         f'<rect x="10.5" y="10.5" width="{W-21}" height="{H-21}" fill="none" stroke="{LINE}" stroke-opacity=".45"/>']
    # general note (the one paragraph)
    nx, nw = 36, 248
    b.append(f'<text x="{nx}" y="46" font-family="{COND}" font-weight="700" font-size="17" fill="{GOLD}">{T("General note")}</text>'
             f'<path d="M{nx} 54H{nx+nw}" stroke="{LINE}" stroke-opacity=".6"/>')
    lines = wrap(general_note(), 15.5, nw)
    for i, line in enumerate(lines):
        b.append(f'<text x="{nx}" y="{80 + i*23}" font-family="{COND}" font-weight="500" font-size="15.5" fill="{LINE}">{T(line)}</text>')
    # BOM table
    tx, tw = 316, W - 316 - 30
    cols = [(tx, "ITEM"), (tx + 52, "ASSEMBLY"), (tx + 190, "PARTS")]
    b.append(f'<path d="M{tx-16} 26V{H-26}" stroke="{LINE}" stroke-opacity=".3"/>')
    for x, lab in cols:
        b.append(f'<text x="{x}" y="44" font-family="{MONO}" font-size="8" fill="{DIM}" letter-spacing="1.5">{T(lab)}</text>')
    b.append(f'<path d="M{tx} 54H{tx+tw}" stroke="{LINE}" stroke-opacity=".6"/>')
    for i, (area, items) in enumerate(rows):
        y = top + i * rh
        cy = y + rh / 2 - 4
        ref = i < 3  # balloons 1-3 on the hero point here
        b.append(balloon(tx + 14, cy, str(i + 1), r=9, size=9, stroke=GOLD if ref else LINE, color=GOLD if ref else LINE))
        b.append(f'<text x="{tx+52}" y="{cy+5}" font-family="{COND}" font-weight="700" font-size="15" fill="{LINE}" letter-spacing=".3">{T(area.upper())}</text>')
        parts = "  ·  ".join(items)
        size = 14
        while text_w(parts, size) > tw - 196 and size > 11:
            size -= .5
        b.append(f'<text x="{tx+190}" y="{cy+5}" font-family="{COND}" font-weight="500" font-size="{size}" fill="{LINE}" fill-opacity=".92">{T(parts)}</text>')
        b.append(f'<path d="M{tx} {y + rh - 4}H{tx+tw}" stroke="{LINE}" stroke-opacity=".16"/>')
    alt = "General note: " + general_note() + " Bill of materials: " + "; ".join(f"{a}: {', '.join(it)}" for a, it in rows)
    return write("bom.svg", svg(W, H, alt, "".join(b), paper_defs(u))), alt


# ------------------------------------------------------------------ sheet 03: detail drawings
def icon(kind, x, y):
    s = f'stroke="{LINE}" stroke-width="1.3" fill="none" stroke-linejoin="round" stroke-linecap="round"'
    if kind == "SITE":  # browser frame in oblique projection
        return (f'<g {s}><path d="M{x} {y+14}l14 -12h54l-14 12z" fill="{LINE}" fill-opacity=".08"/><path d="M{x} {y+14}h54v44h-54z"/>'
                f'<path d="M{x+54} {y+14}l14 -12v44l-14 12"/><path d="M{x} {y+24}h54"/><circle cx="{x+6}" cy="{y+19}" r="1.6"/><circle cx="{x+12}" cy="{y+19}" r="1.6"/>'
                f'<path d="M{x+8} {y+34}h26M{x+8} {y+41}h38M{x+8} {y+48}h20" stroke="{GOLD}"/></g>')
    if kind == "GITHUB":  # terminal with prompt
        return (f'<g {s}><rect x="{x}" y="{y+6}" width="68" height="50" rx="3"/><path d="M{x} {y+16}h68"/>'
                f'<path d="M{x+10} {y+28}l8 6-8 6" stroke="{GOLD}"/><path d="M{x+24} {y+40}h14" stroke="{GOLD}"/>'
                f'<path d="M{x+20} {y+56}v8M{x+48} {y+56}v8M{x+12} {y+64}h44"/></g>')
    if kind == "TENDER":  # document with folded corner + check stamp
        return (f'<g {s}><path d="M{x+8} {y+2}h36l14 14v48h-50z"/><path d="M{x+44} {y+2}v14h14"/>'
                f'<path d="M{x+16} {y+26}h28M{x+16} {y+34}h32M{x+16} {y+42}h20"/>'
                f'<circle cx="{x+50}" cy="{y+52}" r="11" stroke="{GOLD}"/><path d="M{x+45} {y+52}l4 4 7-8" stroke="{GOLD}"/></g>')
    # SIGNAL: mast with broadcast arcs
    return (f'<g {s}><path d="M{x+34} {y+26}l-14 40M{x+34} {y+26}l14 40M{x+25} {y+52}h18"/><circle cx="{x+34}" cy="{y+24}" r="3" stroke="{GOLD}"/>'
            f'<path d="M{x+24} {y+14}a14 14 0 0 0 0 20M{x+44} {y+14}a14 14 0 0 1 0 20M{x+16} {y+6}a26 26 0 0 0 0 36M{x+52} {y+6}a26 26 0 0 1 0 36" stroke="{GOLD}"/></g>')


ICON_FOR = {"kevinm.tech": "SITE", "claude-mods": "GITHUB", "GanhaLic": "TENDER", "Ligado em IA": "SIGNAL"}


def build_detail(i, p, founded):
    H = 132
    u = f"d{i}"
    pw = 640
    ox = 30 + i * 52
    letter = "ABCDEFGH"[i]
    shape = f'<path d="M{ox} 10H{ox+pw-16}L{ox+pw} 26V{H-10}H{ox}Z"/>'
    b = [paper(u, shape), f'<path d="M{ox+.5} 10.5H{ox+pw-16}L{ox+pw-.5} 26V{H-10.5}H{ox+.5}Z" fill="none" stroke="{LINE}" stroke-opacity=".5"/>']
    # detail symbol (letter over sheet number) straddling the plate edge
    cx, cy = ox, 44
    b.append(f'<circle cx="{cx}" cy="{cy}" r="24" fill="{NAVY}" stroke="{GOLD}" stroke-width="1.4"/><path d="M{cx-24} {cy}H{cx+24}" stroke="{GOLD}"/>'
             f'<text x="{cx}" y="{cy-6}" font-family="{COND}" font-weight="700" font-size="18" fill="{GOLD}" text-anchor="middle">{T(letter)}</text>'
             f'<text x="{cx}" y="{cy+15}" font-family="{MONO}" font-weight="500" font-size="9" fill="{GOLD}" text-anchor="middle">{T("03")}</text>')
    tx = ox + 44
    b.append(f'<text x="{tx}" y="52" font-family="{COND}" font-weight="700" font-size="28" fill="{LINE}" letter-spacing="-.3">{T(p["label"])}</text>')
    tagline = p.get("tag", "")
    if p["label"] in founded:
        tagline += "  ·  FOUNDED BY ME"
    host = re.sub(r"^https?://(www\.)?", "", p["url"]).rstrip("/")
    lw = text_w(p["label"], 28, "plex-cond-700.woff2", -.3)
    b.append(f'<text x="{tx + lw + 14:.0f}" y="51" font-family="{MONO}" font-weight="500" font-size="8.5" fill="{GOLD}" letter-spacing="1.4">{T(tagline)}</text>')
    for k, line in enumerate(wrap(p["description"], 14.5, pw - 190)[:2]):
        b.append(f'<text x="{tx}" y="{78 + k*20}" font-family="{COND}" font-weight="500" font-size="14.5" fill="{LINE}" fill-opacity=".9">{T(line)}</text>')
    b.append(f'<text x="{tx}" y="{H-20}" font-family="{MONO}" font-size="8.5" fill="{DIM}" letter-spacing="1">{T(host.upper())}</text>')
    # drawn arrow + icon
    b.append(f'<path d="M{ox+pw-120} {H-23}h30" stroke="{DIM}" marker-end="url(#{u}ar)"/>')
    b.append(icon(ICON_FOR.get(p["label"], "SITE"), ox + pw - 104, 26))
    alt = f"Detail {letter}: {p['label']} ({tagline.title()}). {p['description']}"
    return write(f"detail-{i}.svg", svg(W, H, alt, "".join(b), paper_defs(u))), alt


# ------------------------------------------------------------------ sheet 04: revision history
def build_rev(i, n, post):
    H = 62
    u = f"r{i}"
    letter = "ABCDEFGHIJ"[n - 1 - i]
    latest = i == 0
    b = [paper(u, f'<rect y="2" width="{W}" height="{H-4}"/>'),
         f'<path d="M0 2.5H{W}M0 {H-2.5}H{W}" stroke="{LINE}" stroke-opacity=".35"/>']
    tri = f"M40 {H/2+10}l11-19 11 19z"
    if latest:
        b.append(f'<path class="breathe" d="{tri}" fill="{GOLD}" fill-opacity=".38"/>')
    b.append(f'<path d="{tri}" fill="none" stroke="{GOLD if latest else LINE}" stroke-width="1.3"/>'
             f'<text x="51" y="{H/2+7}" font-family="{MONO}" font-weight="500" font-size="9.5" fill="{GOLD if latest else LINE}" text-anchor="middle">{T(letter)}</text>')
    b.append(f'<text x="86" y="{H/2+4}" font-family="{MONO}" font-weight="500" font-size="10" fill="{DIM}" letter-spacing="1.2">{T(post.get("date", "").upper())}</text>')
    title = post["title"]
    size = 19
    while text_w(title, size, "plex-cond-500.woff2") > 520 and size > 14:
        size -= .5
    b.append(f'<text x="196" y="{H/2+6.5}" font-family="{COND}" font-weight="{700 if latest else 500}" font-size="{size}" fill="{LINE}">{T(title)}</text>')
    b.append(f'<path d="M{W-150} 8V{H-8}" stroke="{LINE}" stroke-opacity=".18"/>'
             f'<text x="{W-136}" y="{H/2-3}" font-family="{MONO}" font-size="7" fill="{DIM}" letter-spacing="1">{T("APPR.")}</text>'
             f'<text x="{W-136}" y="{H/2+11}" font-family="{MONO}" font-weight="500" font-size="10" fill="{LINE}" letter-spacing="1">{T(CFG.get("monogram", ""))}</text>')
    b.append(f'<path d="M{W-74} {H/2}h34" stroke="{GOLD if latest else DIM}" marker-end="url(#{u}ar)"/>')
    b.append(f'<path d="M72 8V{H-8}M182 8V{H-8}" stroke="{LINE}" stroke-opacity=".18"/>')
    alt = f"Revision {letter}, {post.get('date','')}: {title}"
    return write(f"rev-{i}.svg", svg(W, H, alt, "".join(b), paper_defs(u))), alt


def build_all_revs(label):
    H = 52
    u = "ra"
    w = text_w(label, 13, "plex-cond-500.woff2") + 90
    x = W - w
    b = [paper(u, f'<path d="M{x+14} 6H{W}V{H-6}H{x}V20Z"/>'),
         f'<text x="{x+22}" y="{H/2+5}" font-family="{COND}" font-weight="500" font-size="13" fill="{LINE}">{T(label)}</text>'
         f'<path d="M{W-48} {H/2}h26" stroke="{GOLD}" marker-end="url(#{u}ar)"/>']
    return write("all-revisions.svg", svg(W, H, label, "".join(b), paper_defs(u)))


# ------------------------------------------------------------------ sheet 05: stamps
def build_stamp(i, c):
    w, h = 210, 92
    u = f"s{i}"
    rot = [-2.5, 1.8, -1.2, 2.4, -1.8, 1.2][i % 6]
    host = re.sub(r"^(https?://(www\.)?|mailto:)", "", c["url"]).rstrip("/")
    label = c["label"].upper()
    ink = (f'<filter id="{u}ink" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="2" seed="{3+i}" result="n"/>'
           f'<feDisplacementMap in="SourceGraphic" in2="n" scale="0.8" result="d"/><feTurbulence type="fractalNoise" baseFrequency=".35" numOctaves="2" seed="{9+i}"/>'
           f'<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.3 1.75"/><feComposite in="d" operator="in"/></filter>')
    body = (f'<defs>{ink}</defs><g transform="rotate({rot} {w/2} {h/2})">' + paper(u, f'<rect x="12" y="12" width="{w-24}" height="{h-24}" rx="3"/>') +
            f'<g filter="url(#{u}ink)"><rect x="12.5" y="12.5" width="{w-25}" height="{h-25}" rx="3" fill="none" stroke="{GOLD}" stroke-width="2"/>'
            f'<rect x="17.5" y="17.5" width="{w-35}" height="{h-35}" rx="1.5" fill="none" stroke="{GOLD}" stroke-width=".8"/>'
            f'<text x="{w/2}" y="{h/2+3}" font-family="{COND}" font-weight="700" font-size="24" fill="{GOLD}" text-anchor="middle" letter-spacing="2.6">{T(label)}</text></g>'
            f'<text x="{w/2}" y="{h/2+18}" font-family="{MONO}" font-weight="500" font-size="{8 if len(host) < 22 else 7}" fill="{LINE}" text-anchor="middle" letter-spacing=".6">{T(host)}</text></g>')
    return write(f"stamp-{i}.svg", svg(w, h, f"{c['label']}: {host}", body, paper_defs(u)))


# ------------------------------------------------------------------ assemble
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for f in glob.glob(os.path.join(OUT_DIR, "*.svg")):
        os.remove(f)
    hero, hero_alt = build_hero()
    bom, bom_alt = build_bom()
    founded = founded_names()
    md = ["<!--\n  GENERATED by scripts/gen_profile.py. Do not edit by hand.\n"
          "  Edit profile.config.json, then:\n      python3 scripts/fetch_profile_data.py && python3 scripts/gen_profile.py\n"
          "  Art direction: direcao.md (AS-BUILT).\n-->\n",
          f'<p align="center"><img src="{hero}" width="100%" alt="{esc(hero_alt)}" /></p>\n',
          f'<p align="center"><img src="{build_tab("h-bom.svg", 2, "Bill of materials")}" width="100%" alt="Sheet 02: bill of materials" /><br>',
          f'<img src="{bom}" width="100%" alt="{esc(bom_alt)}" /></p>\n',
          f'<p align="center"><img src="{build_tab("h-details.svg", 3, "Detail drawings")}" width="100%" alt="Sheet 03: detail drawings (projects)" /><br>']
    for i, p in enumerate(CFG.get("projects", [])):
        src, alt = build_detail(i, p, founded)
        md.append(f'<a href="{esc(p["url"])}"><img src="{src}" width="100%" alt="{esc(alt)}" /></a><br>')
    md.append("</p>\n")
    posts = DATA.get("posts", [])[: CFG.get("posts", {}).get("count", 3)]
    if posts:
        md.append(f'<p align="center"><img src="{build_tab("h-revisions.svg", 4, "Revision history")}" width="100%" alt="Sheet 04: revision history (latest notes)" /><br>')
        for i, post in enumerate(posts):
            src, alt = build_rev(i, len(posts), post)
            md.append(f'<a href="{esc(post["url"])}"><img src="{src}" width="100%" alt="{esc(alt)}" /></a><br>')
        pc = CFG.get("posts", {})
        if pc.get("all_posts_url"):
            label = pc.get("all_posts_label", "All notes")
            md.append(f'<a href="{esc(pc["all_posts_url"])}"><img src="{build_all_revs(label)}" width="100%" alt="{esc(label)}" /></a>')
        md.append("</p>\n")
    md.append(f'<p align="center"><img src="{build_tab("h-stamps.svg", 5, "Stamps")}" width="100%" alt="Sheet 05: stamps (contact)" /><br>')
    md.append("".join(f'<a href="{esc(c["url"])}"><img src="{build_stamp(i, c)}" height="80" alt="{esc(c["label"])}" /></a>'
                      for i, c in enumerate(CFG.get("contacts", []))))
    md.append("</p>\n")
    with open(os.path.join(ROOT, "README.md"), "w") as f:
        f.write("\n".join(md))
    n = len(glob.glob(os.path.join(OUT_DIR, "*.svg")))
    kb = sum(os.path.getsize(p) for p in glob.glob(os.path.join(OUT_DIR, "*.svg"))) // 1024
    print(f"wrote README.md + {n} SVGs ({kb} KB) in {REL}/")


if __name__ == "__main__":
    main()
