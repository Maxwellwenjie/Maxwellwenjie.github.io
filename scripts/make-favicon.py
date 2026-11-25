#!/usr/bin/env python3
"""
make-favicon.py — render favicon.ico / apple-touch-icon.png from the same
geometry as favicon.svg.

The SVG is the primary icon; these raster versions exist for browsers that
ignore SVG icons and for iOS home-screen shortcuts.

Design: 64-unit grid, rounded square #111827, white W, blue accent bar.

Usage:
    python scripts/make-favicon.py
"""

import os
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Pillow is required:  python -m pip install Pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BG = "#111827"
FG = "#ffffff"
ACCENT = "#2563eb"

# geometry in the 64-unit viewBox, matching favicon.svg
RADIUS = 14
STROKE = 7
POINTS = [(15, 17), (24, 41), (32, 25), (40, 41), (49, 17)]
BAR = (22, 48, 42, 52.5)      # x0, y0, x1, y1
BAR_R = 2.25

SS = 16                        # supersample factor


def render(px):
    """Draw at px * SS then downscale, so edges stay smooth."""
    s = px * SS / 64.0
    size = px * SS
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=RADIUS * s, fill=BG)

    pts = [(x * s, y * s) for x, y in POINTS]
    w = STROKE * s
    d.line(pts, fill=FG, width=int(round(w)), joint="curve")
    r = w / 2.0
    for x, y in pts:
        d.ellipse([x - r, y - r, x + r, y + r], fill=FG)

    x0, y0, x1, y1 = BAR
    d.rounded_rectangle([x0 * s, y0 * s, x1 * s, y1 * s],
                        radius=BAR_R * s, fill=ACCENT)

    return img.resize((px, px), Image.LANCZOS)


def main():
    ico_sizes = [16, 32, 48, 64]
    imgs = {n: render(n) for n in ico_sizes}

    ico_path = os.path.join(ROOT, "favicon.ico")
    imgs[64].save(ico_path, format="ICO",
                  sizes=[(n, n) for n in ico_sizes])
    print("wrote favicon.ico  (%s)" % ", ".join("%dpx" % n for n in ico_sizes))

    touch = render(180)
    touch_path = os.path.join(ROOT, "apple-touch-icon.png")
    touch.save(touch_path, format="PNG", optimize=True)
    print("wrote apple-touch-icon.png (180px)")

    png32 = render(32)
    png32_path = os.path.join(ROOT, "favicon-32.png")
    png32.save(png32_path, format="PNG", optimize=True)
    print("wrote favicon-32.png (32px)")

    for p in (ico_path, touch_path, png32_path):
        print("  %-24s %6d bytes" % (os.path.basename(p), os.path.getsize(p)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
