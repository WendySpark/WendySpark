#!/usr/bin/env python3
"""Turns a photo into an ASCII-art portrait rendered as a plain SVG.

Run once, by hand, against a local photo - not part of the daily stats
refresh. The source photo is never committed; only the generated SVG is.

Usage: python3 scripts/make_portrait.py <path-to-photo> [--cols N]
"""

import argparse
import os

from PIL import Image, ImageOps

# Classic dark-to-light ramp; index 0 renders as nothing (falls back to the
# card background), so only characters print where the source actually has
# tone - which is what makes the portrait look like it's emerging from the
# dark background rather than sitting in a filled rectangle.
RAMP = " .:-=+*#%@"

CHAR_ASPECT = 0.6  # width:height of one rendered character cell (typical monospace advance)
FONT = "ui-monospace, 'JetBrains Mono', 'Fira Code', Consolas, monospace"
COLOR = "#e6edf3"
CELL_PX = 7  # on-screen size of one character cell, before the width= scale


GAMMA = 2.0  # >1 pushes shadows further down, keeping highlights intact -
              # makes dark backgrounds render as empty rather than noisy dots


def build_grid(path, cols):
    im = Image.open(path).convert("L")
    im = ImageOps.autocontrast(im, cutoff=1)
    lut = [round(255 * (v / 255) ** GAMMA) for v in range(256)]
    im = im.point(lut)

    rows = max(1, round(cols * CHAR_ASPECT * im.height / im.width))
    small = im.resize((cols, rows), Image.Resampling.LANCZOS)

    grid = []
    for y in range(rows):
        row = []
        for x in range(cols):
            v = small.getpixel((x, y))  # 0 (dark) .. 255 (bright)
            idx = min(len(RAMP) - 1, v * len(RAMP) // 256)
            row.append(RAMP[idx])
        grid.append(row)
    return grid


def render_svg(grid):
    cols = len(grid[0])
    rows = len(grid)
    cell_w = CELL_PX * CHAR_ASPECT
    width = round(cols * cell_w)
    height = rows * CELL_PX

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    ]
    parts.append(
        f'<text font-family="{FONT}" font-size="{CELL_PX}" fill="{COLOR}" '
        f'xml:space="preserve">'
    )
    for y, row in enumerate(grid):
        line = "".join(row).rstrip()
        if not line.strip():
            continue
        esc = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        parts.append(f'<tspan x="0" y="{(y + 1) * CELL_PX - 1}">{esc}</tspan>')
    parts.append("</text></svg>")
    return "".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="path to the source photo")
    ap.add_argument("--cols", type=int, default=100)
    ap.add_argument(
        "--output",
        default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ascii.svg"),
    )
    args = ap.parse_args()

    grid = build_grid(args.input, args.cols)
    svg = render_svg(grid)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {args.output} ({len(grid[0])}x{len(grid)} characters)")


if __name__ == "__main__":
    main()
