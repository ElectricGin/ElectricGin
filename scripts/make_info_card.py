#!/usr/bin/env python3
"""Hand-author a neofetch-style info card SVG that fades in line by line.

Set STATIC=1 to emit a frozen frame (all lines fully visible) for local
Quick Look / static previews instead of the animated version.
"""
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")
STATIC = os.environ.get("STATIC") == "1"

TITLE = "ElectricGin@github"

ROWS = [
    ("Role", "Student / TBC Officer"),
    ("Now", "SAT prep, robotics + CS projects"),
    ("Stack", "Python, JavaScript, Git, Obsidian + Claude Code"),
    ("Highlights", "Quant backtester, self-hosted MC server,"),
    ("", "email digest agent, PAROL6 robot arm"),
]

WIDTH = 490
LINE_HEIGHT = 26
TOP_PAD = 46
LEFT_PAD = 22
KEY_COLOR = "#39d353"
VAL_COLOR = "#c9d1d9"
BG = "#0d1117"
BORDER = "#30363d"
TITLEBAR = "#161b22"


def main():
    height = TOP_PAD + len(ROWS) * LINE_HEIGHT + 20

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" font-family="ui-monospace, SFMono-Regular, Menlo, monospace">'
    )
    parts.append(f'<rect width="{WIDTH}" height="{height}" rx="8" fill="{BG}" stroke="{BORDER}"/>')
    parts.append(f'<rect width="{WIDTH}" height="28" rx="8" fill="{TITLEBAR}"/>')
    parts.append(f'<rect y="14" width="{WIDTH}" height="14" fill="{TITLEBAR}"/>')
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{16 + i * 16}" cy="14" r="5" fill="{color}"/>')
    parts.append(
        f'<text x="{WIDTH / 2}" y="18" text-anchor="middle" fill="#8b949e" font-size="12">'
        f'{TITLE} &#8212; neofetch</text>'
    )

    if not STATIC:
        parts.append(
            '<style>'
            '.line{opacity:0;transform:translateX(-8px);animation:fadein .4s ease-out forwards;}'
            '@keyframes fadein{to{opacity:1;transform:translateX(0);}}'
            '</style>'
        )

    for i, (key, val) in enumerate(ROWS):
        y = TOP_PAD + i * LINE_HEIGHT
        cls = "" if STATIC else 'class="line" style="animation-delay:%.2fs"' % (i * 0.15)
        if key:
            parts.append(
                f'<text x="{LEFT_PAD}" y="{y}" {cls}>'
                f'<tspan fill="{KEY_COLOR}" font-weight="bold">{key}</tspan>'
                f'<tspan fill="{VAL_COLOR}">: {val}</tspan></text>'
            )
        else:
            parts.append(
                f'<text x="{LEFT_PAD + 78}" y="{y}" {cls} fill="{VAL_COLOR}">{val}</text>'
            )

    parts.append('</svg>')

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
