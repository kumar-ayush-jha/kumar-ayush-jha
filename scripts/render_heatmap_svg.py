#!/usr/bin/env python3
"""
render_heatmap_svg.py — data/contributions.json -> contrib-heatmap.svg

A GitHub-style grid of boxes, monochrome, revealing cell by cell, with a
Less -> More legend and real streak stats printed underneath.

Usage:
    python scripts/render_heatmap_svg.py
"""
import json
from datetime import date, timedelta
from pathlib import Path

IN = Path("data/contributions.json")
OUT = "contrib-heatmap.svg"

CELL = 10
GAP = 3
PAD_X = 20
PAD_TOP = 10
PAD_BOTTOM = 34
WEEKDAY_LABEL_W = 24

# monochrome ramp, light gray -> bright — never rainbow
LEVELS = ["#161b22", "#30363d", "#545d68", "#8b949e", "#c9d1d9"]

REVEAL_DUR = 0.35
REVEAL_STAGGER = 0.004  # per cell, in column-major order


def level_for(count: int, max_count: int) -> int:
    if count == 0:
        return 0
    if max_count <= 0:
        return 1
    ratio = count / max_count
    if ratio > 0.75:
        return 4
    if ratio > 0.5:
        return 3
    if ratio > 0.25:
        return 2
    return 1


def build_svg(data: dict) -> str:
    days = {d["date"]: d["count"] for d in data["days"]}
    if not days:
        raise SystemExit("no contribution days in data — run fetch_contributions.py first")

    all_dates = sorted(days)
    end = date.fromisoformat(all_dates[-1])
    start = date.fromisoformat(all_dates[0])
    # snap start back to the preceding Sunday so columns align to weeks
    start -= timedelta(days=(start.weekday() + 1) % 7)

    max_count = max(days.values()) if days else 0

    weeks = []
    cursor = start
    while cursor <= end:
        week = []
        for _ in range(7):
            key = cursor.isoformat()
            week.append((cursor, days.get(key, 0)))
            cursor += timedelta(days=1)
        weeks.append(week)

    n_weeks = len(weeks)
    width = PAD_X * 2 + WEEKDAY_LABEL_W + n_weeks * (CELL + GAP)
    height = PAD_TOP + 7 * (CELL + GAP) + PAD_BOTTOM

    cells = []
    idx = 0
    for wi, week in enumerate(weeks):
        for di, (d, count) in enumerate(week):
            if d > end:
                continue
            lvl = level_for(count, max_count)
            x = PAD_X + WEEKDAY_LABEL_W + wi * (CELL + GAP)
            y = PAD_TOP + di * (CELL + GAP)
            delay = idx * REVEAL_STAGGER
            idx += 1
            cells.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{LEVELS[lvl]}" style="animation-delay:{delay:.3f}s">'
                f"<title>{d.isoformat()}: {count} contribution{'s' if count != 1 else ''}</title>"
                f"</rect>"
            )

    legend_x = width - PAD_X - (len(LEVELS) * (CELL + GAP)) - 40
    legend_y = height - 16
    legend = [f'<text x="{legend_x - 34}" y="{legend_y + 8}" font-size="10" fill="#8b949e" font-family="SFMono-Regular, Consolas, monospace">Less</text>']
    for i, color in enumerate(LEVELS):
        lx = legend_x + i * (CELL + GAP)
        legend.append(f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>')
    legend.append(
        f'<text x="{legend_x + len(LEVELS) * (CELL + GAP) + 6}" y="{legend_y + 8}" '
        f'font-size="10" fill="#8b949e" font-family="SFMono-Regular, Consolas, monospace">More</text>'
    )

    stats = (
        f"{data.get('total', 0)} contributions in the last year · "
        f"longest streak {data.get('best_streak', 0)} days"
    )

    style = f"""
      .cell {{
        opacity: 0;
        transform-box: fill-box;
        transform-origin: center;
        transform: scale(0.4);
        animation: pop {REVEAL_DUR}s ease-out forwards;
      }}
      @keyframes pop {{
        to {{ opacity: 1; transform: scale(1); }}
      }}
    """

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <style>{style}</style>
  <rect width="100%" height="100%" fill="#0d1117"/>
  <g>
{chr(10).join(cells)}
  </g>
  <text x="{PAD_X}" y="{height - 16}" font-size="11" fill="#8b949e" font-family="SFMono-Regular, Consolas, monospace">{stats}</text>
  <g>{chr(10).join(legend)}</g>
</svg>
"""


def main():
    if not IN.exists():
        raise SystemExit("data/contributions.json not found — run fetch_contributions.py first")
    data = json.loads(IN.read_text())
    svg = build_svg(data)
    Path(OUT).write_text(svg)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
