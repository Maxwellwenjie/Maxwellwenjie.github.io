#!/usr/bin/env python3
"""
optimize-images.py — shrink photos before they go into the repo.

Phone cameras produce 4000-6000px JPEGs of 2-5MB. A web page never needs
more than ~1600px, so resizing cuts the file by roughly 90% with no visible
loss on screen.

Key detail: iPhone photos store rotation in EXIF rather than in the pixel
data. The orientation is baked into the pixels here (exif_transpose) before
resizing, otherwise portrait shots end up sideways once EXIF is dropped.

Usage:
    python scripts/optimize-images.py images/IMG_0065.jpg images/IMG_0243.jpg
    python scripts/optimize-images.py images/ --min-size 400 --dry-run
    python scripts/optimize-images.py images/ --max 1920 --quality 85

Text screenshots (dashboards, terminal output, UI captures) should be left
alone or resized much more gently — shrinking them makes small text
unreadable. Only run this on photographs.
"""

import argparse
import os
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is required:  python -m pip install Pillow")

EXTS = (".jpg", ".jpeg", ".png", ".webp")


def human(n):
    return "%.1fMB" % (n / 1048576) if n >= 1048576 else "%.0fKB" % (n / 1024)


def collect(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for name in sorted(os.listdir(p)):
                if name.lower().endswith(EXTS):
                    out.append(os.path.join(p, name))
        elif os.path.isfile(p):
            out.append(p)
        else:
            print("skip (not found): %s" % p)
    return out


def optimize(path, max_edge, quality, dry_run):
    before = os.path.getsize(path)
    with Image.open(path) as im:
        orig_w, orig_h = im.size
        im = ImageOps.exif_transpose(im)
        w, h = im.size

        scale = min(1.0, max_edge / float(max(w, h)))
        if scale < 1.0:
            im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))),
                           Image.LANCZOS)

        if dry_run:
            import io
            buf = io.BytesIO()
            target = im.convert("RGB") if path.lower().endswith((".jpg", ".jpeg")) else im
            target.save(buf, "JPEG" if path.lower().endswith((".jpg", ".jpeg")) else "PNG",
                        quality=quality, optimize=True, progressive=True)
            after = buf.tell()
        else:
            tmp = path + ".tmp"
            if path.lower().endswith((".jpg", ".jpeg")):
                im.convert("RGB").save(tmp, "JPEG", quality=quality,
                                       optimize=True, progressive=True)
            else:
                im.save(tmp, "PNG", optimize=True)
            after = os.path.getsize(tmp)
            if after >= before:
                os.remove(tmp)
                return path, orig_w, orig_h, before, before, "kept (already optimal)"
            os.replace(tmp, path)

    pct = 100 - after * 100.0 / before
    note = "%.0f%% smaller" % pct if after < before else "no gain"
    return path, orig_w, orig_h, before, after, note


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="image files or directories")
    ap.add_argument("--max", type=int, default=1600, help="long edge in px (default 1600)")
    ap.add_argument("--quality", type=int, default=82, help="JPEG quality (default 82)")
    ap.add_argument("--min-size", type=int, default=0,
                    help="skip files smaller than this many KB")
    ap.add_argument("--dry-run", action="store_true", help="report only, change nothing")
    args = ap.parse_args()

    files = [f for f in collect(args.paths)
             if os.path.getsize(f) >= args.min_size * 1024]
    if not files:
        print("nothing to do")
        return 0

    print("%-26s %-12s %-9s %-9s %s" % ("file", "original", "before", "after", "result"))
    print("-" * 74)
    tot_b = tot_a = 0
    for f in files:
        try:
            path, ow, oh, b, a, note = optimize(f, args.max, args.quality, args.dry_run)
        except Exception as exc:
            print("%-26s ERROR %s" % (os.path.basename(f), exc))
            continue
        tot_b += b
        tot_a += a
        print("%-26s %-12s %-9s %-9s %s"
              % (os.path.basename(path)[:26], "%dx%d" % (ow, oh), human(b), human(a), note))

    print("-" * 74)
    if tot_b:
        print("%-26s %-12s %-9s %-9s %.0f%% smaller"
              % ("TOTAL (%d files)" % len(files), "", human(tot_b), human(tot_a),
                 100 - tot_a * 100.0 / tot_b))
    if args.dry_run:
        print("\n--dry-run: no files were modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
