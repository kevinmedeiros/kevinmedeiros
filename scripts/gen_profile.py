#!/usr/bin/env python3
"""Build the kevinm.tech-styled GitHub profile (SVGs + README.md).

    python3 scripts/gen_profile.py

Inputs : profile.config.json, assets/profile.json, assets/fonts/*.woff2
Outputs: assets/stage/*.svg and README.md (generated — do not hand-edit)

Design read: a Head of DevOps GitHub profile for hiring managers and technical
peers, in the quiet editorial-infra language of kevinm.tech. The characteristic
moment is a GitOps topology, not a stack of identical cards.

GitHub renders SVGs as <img>: CSS animation works, links inside do not. Each
clickable project, note and contact is its own SVG wrapped in <a>. Projects
are laid out as a 2x2 HTML table. Motion is one authored moment (node pulses
and a slow packet on the topology). Content is visible at t=0. prefers-
reduced-motion is honored. Each piece carries its own navy ground so the
profile holds up on GitHub light and dark.
"""
from __future__ import annotations

import base64
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "profile.config.json")))
DATA_PATH = os.path.join(ROOT, "assets", "profile.json")
DATA = json.load(open(DATA_PATH)) if os.path.exists(DATA_PATH) else {}
OUT_DIR = os.path.join(ROOT, "assets", "stage")
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
REL = "assets/stage"

# Designed at the width a GitHub profile README actually paints.
W = 832
PAD = 36
RX = 2

# kevinm.tech dark tokens
BG0 = "#0c1626"
BG1 = "#132033"
BG2 = "#1a2940"
BG3 = "#243650"
TEXT = "#f4f1ea"
MUTED = "#c9d2de"
ACCENT = "#e6c98a"
ACCENT_INK = "#1a1408"
BORDER = "#8fa0b8"
EASE = "cubic-bezier(.22, 1, .36, 1)"

DISPLAY = "'Source Serif 4', 'Source Serif Pro', Georgia, 'Times New Roman', serif"
SANS = "'Source Sans 3', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"


def esc(s):
    return html.escape(str(s), quote=True)


def fmt(n):
    return f"{int(n):,}"


def load_fonts():
    faces = [
        ("Source Serif 4", 500, "normal", "source-serif-4-500-normal.woff2"),
        ("Source Serif 4", 500, "italic", "source-serif-4-500-italic.woff2"),
        ("Source Serif 4", 600, "normal", "source-serif-4-600-normal.woff2"),
        ("Source Sans 3", 400, "normal", "source-sans-3-400-normal.woff2"),
        ("Source Sans 3", 600, "normal", "source-sans-3-600-normal.woff2"),
    ]
    chunks = []
    for family, weight, style, name in faces:
        path = os.path.join(FONT_DIR, name)
        if not os.path.exists(path):
            continue
        b64 = base64.b64encode(open(path, "rb").read()).decode("ascii")
        chunks.append(
            f"@font-face{{font-family:'{family}';font-style:{style};font-weight:{weight};"
            f"font-display:swap;src:url('data:font/woff2;base64,{b64}') format('woff2');}}"
        )
    return "\n".join(chunks)


FONT_CSS = load_fonts()

BASE_CSS = f"""
text {{font-synthesis:none;}}
.pulse {{transform-box:fill-box;transform-origin:center;animation:pulse 2.8s {EASE} infinite;}}
.pulse2 {{transform-box:fill-box;transform-origin:center;animation:pulse 2.8s {EASE} .7s infinite;}}
.pulse3 {{transform-box:fill-box;transform-origin:center;animation:pulse 2.8s {EASE} 1.4s infinite;}}
@keyframes pulse {{
  0%,100% {{opacity:.25; transform:scale(1);}}
  50% {{opacity:.85; transform:scale(1.28);}}
}}
.packet {{
  offset-path: path('M 0 0');
  animation: packet 4.8s {EASE} infinite;
}}
@keyframes packet {{
  0% {{offset-distance:0%; opacity:0;}}
  8% {{opacity:1;}}
  92% {{opacity:1;}}
  100% {{offset-distance:100%; opacity:0;}}
}}
.flow {{stroke-dasharray:5 7; animation:flow 8s linear infinite;}}
@keyframes flow {{to {{stroke-dashoffset:-48;}}}}
@media (prefers-reduced-motion:reduce) {{
  * {{animation-duration:0.01ms !important; animation-iteration-count:1 !important;}}
  .pulse,.pulse2,.pulse3 {{opacity:.45; transform:none;}}
  .flow {{stroke-dasharray:none;}}
}}
"""

SERIF_W = {'a':0.547, 'b':0.624, 'c':0.524, 'd':0.618, 'e':0.536, 'f':0.371, 'g':0.565, 'h':0.645, 'i':0.332, 'j':0.308, 'k':0.604, 'l':0.333, 'm':0.958, 'n':0.647, 'o':0.584, 'p':0.627, 'q':0.607, 'r':0.465, 's':0.47, 't':0.363, 'u':0.634, 'v':0.58, 'w':0.843, 'x':0.577, 'y':0.589, 'z':0.494, 'A':0.712, 'B':0.66, 'C':0.662, 'D':0.742, 'E':0.636, 'F':0.611, 'G':0.724, 'H':0.811, 'I':0.381, 'J':0.387, 'K':0.718, 'L':0.617, 'M':0.933, 'N':0.762, 'O':0.74, 'P':0.629, 'Q':0.74, 'R':0.698, 'S':0.552, 'T':0.641, 'U':0.757, 'V':0.708, 'W':1.012, 'X':0.675, 'Y':0.667, 'Z':0.589, '0':0.538, '1':0.538, '2':0.538, '3':0.538, '4':0.538, '5':0.538, '6':0.538, '7':0.538, '8':0.538, '9':0.538, ' ':0.232, '.':0.304, ',':0.304, ';':0.304, ':':0.304, '!':0.301, '?':0.422, "'":0.194, '"':0.402, '-':0.327, '—':0.821, '–':0.521, '/':0.352, '&':0.733, '+':0.541, '·':0.304, '•':0.312, '%':0.941, '(':0.373, ')':0.373, '[':0.345, ']':0.345, '#':0.535, '@':0.85, '…':0.84, '’':0.23, '“':0.45, '”':0.449, 'ã':0.547, 'á':0.547, 'â':0.547, 'à':0.547, 'é':0.536, 'ê':0.536, 'í':0.332, 'ó':0.584, 'ô':0.584, 'õ':0.584, 'ú':0.634, 'ç':0.524, 'Á':0.712, 'Ã':0.712, 'É':0.636, 'Í':0.381, 'Ó':0.74, 'Ú':0.757, 'Ç':0.662, '~':0.541, '_':0.521}

SANS_W = {'a':0.504, 'b':0.553, 'c':0.456, 'd':0.555, 'e':0.496, 'f':0.292, 'g':0.504, 'h':0.544, 'i':0.246, 'j':0.247, 'k':0.495, 'l':0.255, 'm':0.829, 'n':0.547, 'o':0.542, 'p':0.555, 'q':0.555, 'r':0.347, 's':0.419, 't':0.338, 'u':0.544, 'v':0.467, 'w':0.719, 'x':0.446, 'y':0.467, 'z':0.425, 'A':0.543, 'B':0.588, 'C':0.571, 'D':0.615, 'E':0.527, 'F':0.494, 'G':0.617, 'H':0.652, 'I':0.263, 'J':0.479, 'K':0.579, 'L':0.486, 'M':0.727, 'N':0.647, 'O':0.664, 'P':0.566, 'Q':0.664, 'R':0.569, 'S':0.534, 'T':0.536, 'U':0.645, 'V':0.515, 'W':0.786, 'X':0.513, 'Y':0.476, 'Z':0.539, '0':0.497, '1':0.497, '2':0.497, '3':0.497, '4':0.497, '5':0.497, '6':0.497, '7':0.497, '8':0.497, '9':0.497, ' ':0.2, '.':0.249, ',':0.249, ';':0.249, ':':0.249, '!':0.289, '?':0.425, "'":0.249, '"':0.426, '-':0.311, '—':0.8, '–':0.48, '/':0.35, '&':0.609, '+':0.497, '·':0.249, '•':0.304, '%':0.824, '(':0.303, ')':0.303, '[':0.303, ']':0.303, '#':0.497, '@':0.847, '…':0.948, '’':0.249, '“':0.426, '”':0.426, 'ã':0.504, 'á':0.504, 'â':0.504, 'à':0.504, 'é':0.496, 'ê':0.496, 'í':0.246, 'ó':0.542, 'ô':0.542, 'õ':0.542, 'ú':0.544, 'ç':0.456, 'Á':0.544, 'Ã':0.544, 'É':0.527, 'Í':0.263, 'Ó':0.664, 'Ú':0.645, 'Ç':0.571, '~':0.497, '_':0.5}


def _table(font):
    return SERIF_W if font == "serif" else SANS_W


def text_w(s, size, font="sans"):
    table = _table(font)
    total = 0.0
    for ch in str(s):
        total += table.get(ch, 0.55)
    return total * size


def wrap(s, size, max_w, font="sans"):
    words = str(s).split()
    if not words:
        return []
    lines, cur = [], words[0]
    for word in words[1:]:
        trial = f"{cur} {word}"
        if text_w(trial, size, font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def svg(w, h, title, body, extra_css=""):
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">\n'
        f"<title>{esc(title)}</title>\n"
        f"<defs><style>\n{FONT_CSS}\n{BASE_CSS}\n{extra_css}\n</style></defs>\n"
        f"{body}\n</svg>\n"
    )


def ground(w, h, fill=BG0, corners="none"):
    """corners: none | all | top | bottom. Middle pieces stay square so the board tessellates."""
    if corners == "all":
        return f'<rect width="{w}" height="{h}" fill="{fill}" rx="{RX}"/>'
    if corners == "top":
        return (
            f'<path d="M0,{RX} Q0,0 {RX},0 H{w-RX} Q{w},0 {w},{RX} V{h} H0 Z" fill="{fill}"/>'
        )
    if corners == "bottom":
        return (
            f'<path d="M0,0 H{w} V{h-RX} Q{w},{h} {w-RX},{h} H{RX} Q0,{h} 0,{h-RX} Z" fill="{fill}"/>'
        )
    return f'<rect width="{w}" height="{h}" fill="{fill}"/>'


def write(name, content):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    with open(path, "w") as f:
        f.write(content)
    return path


def stat_items():
    items = [{"value": "9+", "label": "years"}]
    if DATA.get("repos") is not None:
        items.append({"value": str(int(DATA["repos"])), "label": "repos"})
    if DATA.get("followers") is not None:
        items.append({"value": fmt(DATA["followers"]), "label": "followers"})
    if DATA.get("commits") is not None:
        items.append({"value": fmt(DATA["commits"]), "label": "commits"})
    return items[:4]


# --- Topology: a single horizontal GitOps path --------------------------------

def topology(ox, oy, w):
    """Full-width path: Git → CI → Argo → Cluster → Observe. Pulses on cluster nodes."""
    parts = []
    labels = ["Git", "CI", "Argo", "Cluster", "Observe"]
    n = len(labels)
    cy = oy + 14
    left = ox + 28
    right = ox + w - 28
    xs = [left + (right - left) * i / (n - 1) for i in range(n)]

    # connectors stop short of the cluster group
    clear = {"Cluster": 30, "default": 12}
    for (x1, l1), (x2, l2) in zip(zip(xs, labels), zip(xs[1:], labels[1:])):
        gap1 = clear.get(l1, clear["default"])
        gap2 = clear.get(l2, clear["default"])
        parts.append(
            f'<line class="flow" x1="{x1 + gap1}" y1="{cy}" x2="{x2 - gap2}" y2="{cy}" '
            f'stroke="{ACCENT}" stroke-width="1.2" stroke-opacity="0.55"/>'
        )

    for x, lab in zip(xs, labels):
        if lab == "Cluster":
            offsets = [(-20, 0), (0, 0), (20, 0)]
            pcls = ["pulse", "pulse2", "pulse3"]
            for (dx, dy), pc in zip(offsets, pcls):
                parts.append(
                    f'<circle class="{pc}" cx="{x+dx}" cy="{cy+dy}" r="10" fill="none" '
                    f'stroke="{ACCENT}" stroke-width="1"/>'
                )
                parts.append(f'<circle cx="{x+dx}" cy="{cy+dy}" r="5" fill="{ACCENT}"/>')
            parts.append(
                f'<text x="{x}" y="{cy + 36}" text-anchor="middle" fill="{TEXT}" '
                f'font-family="{SANS}" font-size="15">{esc(lab)}</text>'
            )
        else:
            parts.append(f'<circle cx="{x}" cy="{cy}" r="6.5" fill="{ACCENT}"/>')
            parts.append(
                f'<text x="{x}" y="{cy + 36}" text-anchor="middle" fill="{TEXT}" '
                f'font-family="{SANS}" font-size="15">{esc(lab)}</text>'
            )
    return "\n".join(parts), 62


# --- Marks
# --- Marks for the four projects (consistent 1.4px gold stroke) ------------

def mark_site(x, y, s=36):
    # a simple window / page
    return (
        f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{RX}" fill="none" stroke="{ACCENT}" stroke-width="1.4"/>'
        f'<rect x="{x + 6}" y="{y + 8}" width="{s - 12}" height="3" fill="{ACCENT}"/>'
        f'<rect x="{x + 6}" y="{y + 15}" width="{s - 18}" height="2" fill="{ACCENT}" opacity="0.7"/>'
        f'<rect x="{x + 6}" y="{y + 20}" width="{s - 22}" height="2" fill="{ACCENT}" opacity="0.5"/>'
        f'<rect x="{x + 6}" y="{y + 25}" width="{s - 14}" height="2" fill="{ACCENT}" opacity="0.4"/>'
    )


def mark_mods(x, y, s=36):
    # terminal with a prompt
    return (
        f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{RX}" fill="none" stroke="{ACCENT}" stroke-width="1.4"/>'
        f'<text x="{x + 7}" y="{y + 23}" fill="{ACCENT}" font-family="{SANS}" font-size="13" font-weight="600">~/</text>'
    )


def mark_tender(x, y, s=36):
    # document with a check
    return (
        f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{RX}" fill="none" stroke="{ACCENT}" stroke-width="1.4"/>'
        f'<path d="M{x+10},{y+19} l5 5 11-12" fill="none" stroke="{ACCENT}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def mark_signal(x, y, s=36):
    # concentric broadcast
    cx, cy = x + s / 2, y + s / 2
    return (
        f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{RX}" fill="none" stroke="{ACCENT}" stroke-width="1.4"/>'
        f'<circle cx="{cx}" cy="{cy}" r="3" fill="{ACCENT}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="7.5" fill="none" stroke="{ACCENT}" stroke-width="1.2"/>'
        f'<circle cx="{cx}" cy="{cy}" r="12" fill="none" stroke="{ACCENT}" stroke-width="1.1" opacity="0.6"/>'
    )


MARKS = [mark_site, mark_mods, mark_tender, mark_signal]


def build_hero():
    name = CFG["name"]
    role = CFG["role"]
    handle = CFG.get("prompt") or "kevinmedeiros"
    monogram = CFG["monogram"]
    loc = CFG.get("location") or ""
    intro = CFG["intro"]
    quote = CFG.get("pull_quote") or ""
    founded = CFG.get("founded") or ""
    lead = CFG["tagline_lead"]
    accent = CFG["tagline_accent"]
    rest = CFG["tagline_rest"]

    title_size = 52
    title_lh = 56
    intro_size = 17
    intro_lh = 26
    quote_size = 20
    text_max = W - PAD * 2

    quote_lines = wrap(quote, quote_size, text_max, font="serif") if quote else []
    intro_lines = wrap(intro, intro_size, text_max, font="sans")
    founded_lines = wrap(founded, intro_size, text_max, font="sans") if founded else []

    y = PAD
    y_title = y + 44 + 26
    y_quote = y_title + title_lh * 2 + 18
    y_intro = y_quote + 28 * len(quote_lines) + (10 if quote_lines else 0)
    text_bottom = y_intro + intro_lh * len(intro_lines) + (10 + intro_lh * len(founded_lines) if founded_lines else 0)
    y_diag = text_bottom + 28
    _, diag_h = topology(0, 0, 100)  # height only
    y_rule = y_diag + diag_h + 18
    y_stats = y_rule + 36
    h = y_stats + 48 + PAD - 10

    parts = [ground(W, h, corners="top")]

    # monogram
    ms = 40
    parts.append(
        f'<rect x="{PAD}" y="{y}" width="{ms}" height="{ms}" fill="none" stroke="{ACCENT}" stroke-width="1.2" rx="{RX}"/>'
        f'<text x="{PAD + ms/2}" y="{y + 27}" text-anchor="middle" fill="{ACCENT}" '
        f'font-family="{DISPLAY}" font-weight="600" font-size="16">{esc(monogram)}</text>'
    )
    px = PAD + ms + 14
    parts.append(
        f'<text x="{px}" y="{y + 17}" fill="{TEXT}" font-family="{SANS}" font-weight="600" font-size="16">{esc(handle)}</text>'
    )
    parts.append(
        f'<text x="{px}" y="{y + 35}" fill="{MUTED}" font-family="{SANS}" font-size="15">{esc(role)}</text>'
    )
    if loc:
        parts.append(
            f'<text x="{W - PAD}" y="{y + 26}" text-anchor="end" fill="{MUTED}" '
            f'font-family="{SANS}" font-size="15">{esc(loc)}</text>'
        )

    # title
    parts.append(
        f'<text x="{PAD}" y="{y_title + 40}" fill="{TEXT}" font-family="{DISPLAY}" '
        f'font-weight="500" font-size="{title_size}" letter-spacing="-0.03em">{esc(lead)}</text>'
    )
    parts.append(
        f'<text x="{PAD}" y="{y_title + title_lh + 40}" fill="{TEXT}" font-family="{DISPLAY}" '
        f'font-weight="500" font-size="{title_size}" letter-spacing="-0.03em">'
        f'<tspan fill="{ACCENT}" font-style="italic">{esc(accent)}</tspan>{esc(rest)}</text>'
    )

    for i, line in enumerate(quote_lines):
        parts.append(
            f'<text x="{PAD}" y="{y_quote + i * 28}" fill="{TEXT}" font-family="{DISPLAY}" '
            f'font-style="italic" font-weight="500" font-size="{quote_size}">{esc(line)}</text>'
        )
    for i, line in enumerate(intro_lines):
        parts.append(
            f'<text x="{PAD}" y="{y_intro + i * intro_lh}" fill="{TEXT}" font-family="{SANS}" '
            f'font-size="{intro_size}">{esc(line)}</text>'
        )
    fy = y_intro + intro_lh * len(intro_lines) + 10
    for i, line in enumerate(founded_lines):
        parts.append(
            f'<text x="{PAD}" y="{fy + i * intro_lh}" fill="{TEXT}" font-family="{SANS}" '
            f'font-size="{intro_size}">{esc(line)}</text>'
        )

    # full-width GitOps path, under the copy
    drawn, _ = topology(PAD, y_diag, W - PAD * 2)
    parts.append(drawn)

    # stats
    parts.append(
        f'<rect x="{PAD}" y="{y_rule}" width="{W - PAD * 2}" height="1" fill="{BG3}"/>'
    )
    items = stat_items()
    col_w = (W - PAD * 2) / max(len(items), 1)
    for i, it in enumerate(items):
        cx = PAD + col_w * i
        parts.append(
            f'<text x="{cx}" y="{y_stats + 8}" fill="{ACCENT}" font-family="{DISPLAY}" '
            f'font-weight="500" font-size="40" letter-spacing="-0.03em">{esc(it["value"])}</text>'
        )
        parts.append(
            f'<text x="{cx}" y="{y_stats + 32}" fill="{MUTED}" font-family="{SANS}" '
            f'font-size="15">{esc(it["label"])}</text>'
        )

    alt = (
        f"{name}, {role}. {lead} {accent}{rest} "
        + (quote + " " if quote else "")
        + intro + " "
        + (founded + " " if founded else "")
        + " · ".join(f"{it['value']} {it['label']}" for it in items)
        + f" {loc}"
    )
    write("hero.svg", svg(W, h, alt, "\n".join(parts)))
    return alt, h


def build_stack():
    groups = CFG.get("stack") or []
    title = "Stack"
    # two columns
    mid = 3  # denser groups on the left
    left, right = groups[:mid], groups[mid:]
    col_w = (W - PAD * 2 - 24) / 2
    chip_size = 15
    chip_h = 28
    row_gap = 8
    cat_gap = 18

    def measure_group(g, width):
        y = 18  # category label
        x = 0
        lines = 1
        for item in g["items"]:
            cw = 16 + text_w(item, chip_size, "sans") + 16
            if x and x + cw > width:
                x = 0
                lines += 1
            x += cw + 8
        return 18 + lines * (chip_h + row_gap)

    def col_height(gs, width):
        return sum(measure_group(g, width) + cat_gap for g in gs) - cat_gap

    body_h = max(col_height(left, col_w), col_height(right, col_w))
    y0 = PAD + 8
    h = y0 + 28 + body_h + PAD

    parts = [ground(W, h)]
    parts.append(
        f'<text x="{PAD}" y="{y0 + 16}" fill="{TEXT}" font-family="{DISPLAY}" '
        f'font-weight="500" font-size="24">{esc(title)}</text>'
    )

    def paint_groups(gs, x0, y_start, width):
        y = y_start
        for g in gs:
            parts.append(
                f'<text x="{x0}" y="{y + 14}" fill="{ACCENT}" font-family="{SANS}" '
                f'font-weight="600" font-size="15">{esc(g["area"])}</text>'
            )
            x = x0
            y_chip = y + 22
            for item in g["items"]:
                cw = 16 + text_w(item, chip_size, "sans") + 16
                if x > x0 and x + cw > x0 + width:
                    x = x0
                    y_chip += chip_h + row_gap
                parts.append(
                    f'<rect x="{x}" y="{y_chip}" width="{cw}" height="{chip_h}" rx="{RX}" '
                    f'fill="{BG1}" stroke="{BG3}" stroke-width="1"/>'
                )
                parts.append(
                    f'<text x="{x + cw/2}" y="{y_chip + 19}" text-anchor="middle" fill="{TEXT}" '
                    f'font-family="{SANS}" font-size="{chip_size}">{esc(item)}</text>'
                )
                x += cw + 8
            y = y_chip + chip_h + cat_gap

    paint_groups(left, PAD, y0 + 36, col_w)
    paint_groups(right, PAD + col_w + 24, y0 + 36, col_w)

    alt = "Stack: " + "; ".join(f"{g['area']}: " + ", ".join(g["items"]) for g in groups)
    write("stack.svg", svg(W, h, alt, "\n".join(parts)))
    return alt, h


def build_work_head():
    h = 52
    parts = [ground(W, h)]
    parts.append(
        f'<text x="{PAD}" y="{PAD + 4}" fill="{TEXT}" font-family="{DISPLAY}" '
        f'font-weight="500" font-size="24">Work</text>'
    )
    write("h-work.svg", svg(W, h, "Work", "\n".join(parts)))
    return h


def build_project(i, proj, tw, th):
    title = proj["label"]
    desc = proj.get("description") or ""
    title_size = 22
    body_size = 16
    max_w = tw - 28 - 36 - 16  # leave room for the mark
    # title usually one line
    title_lines = wrap(title, title_size, tw - 56, font="serif")
    desc_lines = wrap(desc, body_size, tw - 56, font="sans")[:3]

    parts = [ground(tw, th, BG1, corners="all")]
    parts.append(
        f'<rect x="0.5" y="0.5" width="{tw-1}" height="{th-1}" fill="none" stroke="{BG3}" stroke-width="1" rx="{RX}"/>'
    )
    # mark
    parts.append(MARKS[i % len(MARKS)](20, 22, 36))
    # title next to / below mark? Title to the right of mark on first line feels crowded
    # Place mark top-left, title to its right, desc below both.
    tx = 20 + 36 + 14
    ty = 22 + 24
    # If title is long, put it under the mark instead
    if text_w(title, title_size, "serif") > tw - 56 - 50:
        tx = 20
        ty = 22 + 36 + 28
        desc_top = ty + 14
        title_lines = wrap(title, title_size, tw - 40, font="serif")
    else:
        desc_top = 22 + 36 + 18
        title_lines = [title]

    for j, line in enumerate(title_lines):
        parts.append(
            f'<text x="{tx if j == 0 else 20}" y="{ty + j * 26}" fill="{TEXT}" '
            f'font-family="{DISPLAY}" font-weight="500" font-size="{title_size}">{esc(line)}</text>'
        )
    # If title was one line beside the mark, desc starts under the mark row
    for j, line in enumerate(desc_lines):
        parts.append(
            f'<text x="20" y="{desc_top + j * 24}" fill="{MUTED}" '
            f'font-family="{SANS}" font-size="{body_size}">{esc(line)}</text>'
        )

    alt = f"{title}: {desc}"
    write(f"project-{i}.svg", svg(tw, th, alt, "\n".join(parts)))
    return alt


def build_notes_head():
    h = 52
    parts = [ground(W, h)]
    parts.append(
        f'<text x="{PAD}" y="{PAD + 4}" fill="{TEXT}" font-family="{DISPLAY}" '
        f'font-weight="500" font-size="24">Notes</text>'
    )
    write("h-notes.svg", svg(W, h, "Notes", "\n".join(parts)))
    return h


def build_post(i, post, last=False):
    date = post.get("date") or ""
    title = post["title"]
    desc = post.get("description") or ""
    h = 58
    date_w = 92
    parts = [ground(W, h, BG0)]
    # top hairline to form a list, not a card
    parts.append(f'<rect x="{PAD}" y="0" width="{W - PAD * 2}" height="1" fill="{BG3}"/>')
    if date:
        parts.append(
            f'<text x="{PAD}" y="{36}" fill="{ACCENT}" font-family="{SANS}" '
            f'font-weight="600" font-size="15">{esc(date)}</text>'
        )
    title_max = W - PAD * 2 - date_w - 8
    # one line only, ellipsis if needed
    t = title
    if text_w(t, 17, "serif") > title_max:
        while t and text_w(t + "…", 17, "serif") > title_max:
            t = t[:-1]
        t = t.rstrip() + "…"
    parts.append(
        f'<text x="{PAD + date_w}" y="{36}" fill="{TEXT}" font-family="{DISPLAY}" '
        f'font-weight="500" font-size="17">{esc(t)}</text>'
    )
    alt = f"{date} — {title}. {desc}".strip(" —.")
    write(f"post-{i}.svg", svg(W, h, alt, "\n".join(parts)))
    return alt


def build_all_posts(label):
    h = 62
    parts = [ground(W, h, BG0, corners="bottom")]
    parts.append(f'<rect x="{PAD}" y="0" width="{W - PAD * 2}" height="1" fill="{BG3}"/>')
    parts.append(
        f'<text x="{PAD}" y="{36}" fill="{ACCENT}" font-family="{DISPLAY}" '
        f'font-weight="500" font-size="17">{esc(label)}</text>'
    )
    write("all-posts.svg", svg(W, h, label, "\n".join(parts)))
    return label


def build_contact(i, contact, primary=False):
    label = contact["label"]
    size = 16
    pad_x = 22
    tw = int(text_w(label, size, "sans") + pad_x * 2)
    tw = max(tw, 128)
    h = 48
    if primary:
        body = (
            f'<rect width="{tw}" height="{h}" fill="{ACCENT}" rx="{RX}"/>'
            f'<text x="{tw/2}" y="{31}" text-anchor="middle" fill="{ACCENT_INK}" '
            f'font-family="{SANS}" font-weight="600" font-size="{size}">{esc(label)}</text>'
        )
    else:
        body = (
            f'<rect width="{tw}" height="{h}" fill="{BG1}" stroke="{BORDER}" stroke-width="1" rx="{RX}"/>'
            f'<text x="{tw/2}" y="{31}" text-anchor="middle" fill="{TEXT}" '
            f'font-family="{SANS}" font-weight="600" font-size="{size}">{esc(label)}</text>'
        )
    write(f"contact-{i}.svg", svg(tw, h, label, body))
    return tw, label


def build_contact_bar():
    """A slim ground that visually closes the board; buttons sit under it in HTML."""
    h = 28
    parts = [ground(W, h)]
    # just a closing cap so the last list row doesn't feel cut
    write("h-contact.svg", svg(W, h, "Get in touch", "\n".join(parts)))
    return h


def build_readme(hero_alt, stack_alt, project_alts, post_alts):
    def img(name, alt, width="100%"):
        return f'<img src="{REL}/{name}" width="{width}" alt="{esc(alt)}" />'

    lines = [
        "<!--",
        "  GENERATED by scripts/gen_profile.py. Do not edit by hand.",
        "  Edit profile.config.json, then:",
        "      python3 scripts/fetch_profile_data.py && python3 scripts/gen_profile.py",
        "  The Refresh profile Action does this daily.",
        "-->",
        "",
        f'<p align="center">{img("hero.svg", hero_alt)}<br />{img("stack.svg", stack_alt)}</p>',
        "",
        f'<p align="center">{img("h-work.svg", "Work")}</p>',
        '<table width="100%" border="0" cellspacing="0" cellpadding="0">',
    ]
    projects = CFG["projects"]
    # 2x2
    for row in range(0, len(projects), 2):
        lines.append("<tr>")
        for col in range(2):
            idx = row + col
            if idx >= len(projects):
                lines.append('<td width="50%"></td>')
                continue
            proj = projects[idx]
            gap = ' style="padding-left:8px;"' if col == 1 else ' style="padding-right:8px;padding-bottom:8px;"'
            if col == 1:
                gap = ' style="padding-left:8px;padding-bottom:8px;"'
            else:
                gap = ' style="padding-right:8px;padding-bottom:8px;"'
            lines.append(
                f'<td width="50%" valign="top"{gap}>'
                f'<a href="{esc(proj["url"])}">{img(f"project-{idx}.svg", project_alts[idx])}</a>'
                f"</td>"
            )
        lines.append("</tr>")
    lines += [
        "</table>",
        "",
        '<p align="center">',
        img("h-notes.svg", "Notes") + "<br />",
    ]
    posts = DATA.get("posts") or []
    for i, post in enumerate(posts):
        lines.append(f'<a href="{esc(post["url"])}">{img(f"post-{i}.svg", post_alts[i])}</a><br />')
    all_label = CFG.get("posts", {}).get("all_posts_label", "All notes")
    all_url = CFG.get("posts", {}).get("all_posts_url", "https://kevinm.tech/blog/")
    lines.append(f'<a href="{esc(all_url)}">{img("all-posts.svg", all_label)}</a>')
    lines.append("</p>")
    lines.append("")
    lines.append('<p align="center">')
    contact_bits = []
    for i, c in enumerate(CFG.get("contacts") or []):
        contact_bits.append(
            f'<a href="{esc(c["url"])}">{img(f"contact-{i}.svg", c["label"], width="auto")}</a>'
        )
    lines.append("&nbsp;&nbsp;".join(contact_bits))
    lines += ["</p>", ""]
    path = os.path.join(ROOT, "README.md")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path


def main():
    # clear stale stage files from the previous design
    if os.path.isdir(OUT_DIR):
        for name in os.listdir(OUT_DIR):
            if name.endswith(".svg"):
                os.remove(os.path.join(OUT_DIR, name))

    hero_alt, _ = build_hero()
    stack_alt, _ = build_stack()
    build_work_head()
    # project tiles: 2-col, same height
    gap = 8
    tw = int((W - gap) / 2)
    th = 184
    project_alts = [build_project(i, p, tw, th) for i, p in enumerate(CFG["projects"])]
    build_notes_head()
    posts = DATA.get("posts") or []
    post_alts = [build_post(i, p) for i, p in enumerate(posts)]
    build_all_posts(CFG.get("posts", {}).get("all_posts_label", "All notes"))
    for i, c in enumerate(CFG.get("contacts") or []):
        build_contact(i, c, primary=(i == 0))
    path = build_readme(hero_alt, stack_alt, project_alts, post_alts)
    print(f"Wrote SVGs to {OUT_DIR} and {path}")


if __name__ == "__main__":
    main()
