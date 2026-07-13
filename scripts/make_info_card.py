#!/usr/bin/env python3
"""
make_info_card.py — ROWS + HOST -> info-card.svg

A neofetch-style panel: "user@host" header, a divider, then key: value rows.
Edit ROWS and HOST below and re-run. Keep it the same visual height as the
portrait (matched via H); if it overflows, bump H and re-match `width=` /
implicit height in the profile README.
"""
from pathlib import Path

# ---- EDIT ME ---------------------------------------------------------------
HOST = "ayush@devbox"

ROWS = [
    ("Role", "Full Stack Developer (MERN)"),
    ("Experience", "~3 years across 4 companies"),
    ("Currently", "Mindstein Software — Jan 2026 to Present"),
    ("Studying", "MCA @ Lovely Professional University"),
    ("Stack", "React.js · Next.js · Node.js · Django"),
    ("Also", "Express · MongoDB · PostgreSQL · Tailwind"),
    ("Shipped", "GigFlow · MicroCourses · NyayDetect"),
    ("Focus", "ATS-ready, achievement-driven engineering"),
]
# -----------------------------------------------------------------------------

OUT = "info-card.svg"

W = 490
H = 300           # keep in sync with the portrait's rendered height
PAD_X = 22
PAD_TOP = 34
LINE_H = 24
LABEL_COLOR = "#58a6ff"
VALUE_COLOR = "#c9d1d9"
MUTED_COLOR = "#8b949e"
BG = "#0d1117"
RULE_COLOR = "#21262d"
FONT_SIZE = 13
HEADER_SIZE = 15


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg() -> str:
    label_w = max(len(k) for k, _ in ROWS)

    parts = []
    parts.append(
        f'<text x="{PAD_X}" y="{PAD_TOP}" font-family="SFMono-Regular, Consolas, monospace" '
        f'font-size="{HEADER_SIZE}" fill="{LABEL_COLOR}" font-weight="bold">{esc(HOST)}</text>'
    )
    rule_y = PAD_TOP + 12
    parts.append(
        f'<line x1="{PAD_X}" y1="{rule_y}" x2="{W - PAD_X}" y2="{rule_y}" '
        f'stroke="{RULE_COLOR}" stroke-width="1"/>'
    )

    y = rule_y + 30
    for i, (label, value) in enumerate(ROWS):
        row_id = f"row{i}"
        delay = 0.15 + i * 0.09
        parts.append(
            f'<g class="fadein" style="animation-delay:{delay:.2f}s">'
            f'<text x="{PAD_X}" y="{y}" font-family="SFMono-Regular, Consolas, monospace" '
            f'font-size="{FONT_SIZE}" fill="{LABEL_COLOR}">{esc(label)}</text>'
            f'<text x="{PAD_X + (label_w + 2) * 7.2}" y="{y}" '
            f'font-family="SFMono-Regular, Consolas, monospace" font-size="{FONT_SIZE}" '
            f'fill="{VALUE_COLOR}">{esc(value)}</text>'
            f"</g>"
        )
        y += LINE_H

    style = """
      .fadein { opacity: 0; animation: fadein 0.5s ease-out forwards; }
      @keyframes fadein {
        from { opacity: 0; transform: translateX(-4px); }
        to   { opacity: 1; transform: translateX(0); }
      }
    """

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <style>{style}</style>
  <rect width="100%" height="100%" rx="6" fill="{BG}" stroke="{RULE_COLOR}"/>
{chr(10).join(parts)}
  <text x="{PAD_X}" y="{H - 14}" font-family="SFMono-Regular, Consolas, monospace" font-size="11" fill="{MUTED_COLOR}">updated daily · see contribution graph below</text>
</svg>
"""


def main():
    Path(OUT).write_text(build_svg())
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
