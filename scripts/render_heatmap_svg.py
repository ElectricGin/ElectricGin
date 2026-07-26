#!/usr/bin/env python3
"""Render data/contributions.json as an animated SVG contribution heatmap."""
import datetime
import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")
STATIC = os.environ.get("STATIC") == "1"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 11
GAP = 3
LEFT_PAD = 28
TOP_PAD = 30
BOTTOM_PAD = 46
WEEKS = 53
DAYS = 7


def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_grid(days):
    by_date = {d["date"]: d["level"] for d in days}
    today = datetime.date.today()
    # end on the most recent Saturday so the grid lines up like GitHub's
    end = today
    start = end - datetime.timedelta(weeks=WEEKS - 1)
    start -= datetime.timedelta(days=(start.weekday() + 1) % 7)  # back up to a Sunday

    grid = []
    cursor = start
    for week in range(WEEKS):
        col = []
        for day in range(DAYS):
            date_str = cursor.isoformat()
            level = by_date.get(date_str, 0)
            col.append((date_str, level))
            cursor += datetime.timedelta(days=1)
        grid.append(col)
    return grid


def main():
    data = load_data()
    grid = build_grid(data["days"])
    stats = data["stats"]
    total = stats["total_active_days"]

    width = LEFT_PAD + WEEKS * (CELL + GAP)
    height = TOP_PAD + DAYS * (CELL + GAP) + BOTTOM_PAD

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace">'
    )
    parts.append(f'<rect width="{width}" height="{height}" fill="#0d1117" rx="8"/>')
    if not STATIC:
        parts.append(
            '<style>'
            '.cell{opacity:0;transform:translate(-6px,-6px);animation:reveal .35s ease-out forwards;}'
            '@keyframes reveal{to{opacity:1;transform:translate(0,0);}}'
            '</style>'
        )

    delay_step = 0.008
    for w, col in enumerate(grid):
        for d, (date_str, level) in enumerate(col):
            x = LEFT_PAD + w * (CELL + GAP)
            y = TOP_PAD + d * (CELL + GAP)
            color = PALETTE[min(level, len(PALETTE) - 1)]
            delay = (w + d) * delay_step
            if STATIC:
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}">'
                    f'<title>{date_str}: level {level}</title></rect>'
                )
            else:
                parts.append(
                    f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                    f'fill="{color}" style="animation-delay:{delay:.3f}s">'
                    f'<title>{date_str}: level {level}</title></rect>'
                )

    legend_y = TOP_PAD + DAYS * (CELL + GAP) + 18
    legend_x = LEFT_PAD
    parts.append(
        f'<text x="{legend_x}" y="{legend_y}" fill="#8b949e" font-size="11">Less</text>'
    )
    lx = legend_x + 38
    for level, color in enumerate(PALETTE):
        parts.append(f'<rect x="{lx}" y="{legend_y - 10}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>')
        lx += CELL + GAP
    parts.append(f'<text x="{lx + 4}" y="{legend_y}" fill="#8b949e" font-size="11">More</text>')

    footer_y = legend_y + 20
    parts.append(
        f'<text x="{legend_x}" y="{footer_y}" fill="#c9d1d9" font-size="12">'
        f'{total} contributions in the last year &#183; current streak {stats["current_streak"]}d '
        f'&#183; longest streak {stats["longest_streak"]}d</text>'
    )

    parts.append('</svg>')

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
