#!/usr/bin/env python3
"""
make_ascii_svg.py — source-prepped.png -> avi-ascii.svg

Samples the prepped (background-removed, CLAHE'd) photo into a grid, maps
brightness to an ASCII ramp, and lays it out as monochrome <text> rows inside
an SVG. Each row "types" itself in with a CSS animation, staggered so the
whole portrait builds top -> bottom like a terminal.

Usage:
    python scripts/make_ascii_svg.py
    STATIC=1 python scripts/make_ascii_svg.py   # bakes the final frame, no animation
"""
import os
from pathlib import Path

import numpy as np
from PIL import Image

# ---- tuning ---------------------------------------------------------------
SRC = "source-prepped.png"
OUT = "avi-ascii.svg"

COLS = 90              # ascii grid width (characters)
ROWS_ = None            # None = derive from image aspect ratio via CHAR_ASPECT
CHAR_ASPECT = 0.55      # terminal glyphs are taller than wide; corrects sampling

CONTRAST = 1.15         # post-sample contrast multiplier
GAMMA = 0.9             # <1 brightens midtones, >1 darkens them
WHITE_FLOOR = 18        # brightness (0-255) below which we treat as pure background -> space

FONT_SIZE = 7
LINE_HEIGHT = FONT_SIZE * 1.0
COLOR = "#8b949e"       # single monochrome gray — never per-character color

ROW_DUR = 0.6           # seconds for one row to "type" in
STAGGER = 0.045         # seconds between each row starting

# darkest -> lightest
RAMP = " .:-=+*#%@"
STATIC = os.environ.get("STATIC", "0") == "1"
# -----------------------------------------------------------------------------


def load_gray(path: str):
    img = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", img.size, (13, 17, 23, 255))  # GitHub dark bg
    composited = Image.alpha_composite(bg, img).convert("L")
    return composited


def sample_ascii(gray: Image.Image, cols: int) -> list[str]:
    w, h = gray.size
    rows = ROWS_ or max(1, round(cols * (h / w) * CHAR_ASPECT))
    small = gray.resize((cols, rows), Image.LANCZOS)
    arr = np.asarray(small, dtype=np.float32)

    arr = np.clip((arr - 127.5) * CONTRAST + 127.5, 0, 255)
    arr = 255 * ((arr / 255) ** GAMMA)
    arr[arr < WHITE_FLOOR] = 0

    idx = np.clip((arr / 255 * (len(RAMP) - 1)).round().astype(int), 0, len(RAMP) - 1)
    lines = ["".join(RAMP[i] for i in row) for row in idx]
    return lines


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(lines: list[str]) -> str:
    cols = max(len(l) for l in lines)
    width = round(cols * FONT_SIZE * 0.62)
    height = round(len(lines) * LINE_HEIGHT) + 10

    style = f"""
      text {{
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: {FONT_SIZE}px;
        fill: {COLOR};
        white-space: pre;
      }}
    """
    if not STATIC:
        style += """
      tspan.row {
        opacity: 0;
        animation: reveal 0.01s forwards;
      }
    """

    rows_svg = []
    for i, line in enumerate(lines):
        y = 12 + i * LINE_HEIGHT
        delay = i * STAGGER
        if STATIC:
            rows_svg.append(f'<text x="4" y="{y:.1f}">{esc(line)}</text>')
        else:
            # typewriter reveal: clip-path sweeps left -> right per row via CSS width trick
            rows_svg.append(
                f'<text x="4" y="{y:.1f}" class="row" '
                f'style="animation: type {ROW_DUR}s steps({max(len(line),1)}) {delay:.3f}s forwards;">'
                f"{esc(line)}</text>"
            )

    keyframes = ""
    if not STATIC:
        keyframes = f"""
      text.row {{
        opacity: 0;
        overflow: hidden;
      }}
      @keyframes type {{
        0%   {{ opacity: 1; clip-path: inset(0 100% 0 0); }}
        1%   {{ opacity: 1; }}
        100% {{ opacity: 1; clip-path: inset(0 0 0 0); }}
      }}
    """

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <style>{style}{keyframes}</style>
  <rect width="100%" height="100%" fill="#0d1117"/>
  <g>
{chr(10).join(rows_svg)}
  </g>
</svg>
"""


def main():
    src = Path(SRC)
    if not src.exists():
        raise SystemExit(
            f"error: {SRC} not found — run prep_photo.py first:\n"
            f"  python scripts/prep_photo.py <your photo> {SRC}"
        )
    gray = load_gray(str(src))
    lines = sample_ascii(gray, COLS)
    svg = build_svg(lines)
    Path(OUT).write_text(svg)
    print(f"wrote {OUT}  ({len(lines)} rows x {COLS} cols, static={STATIC})")


if __name__ == "__main__":
    main()
