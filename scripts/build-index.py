#!/usr/bin/env python3
"""
build-index.py — regenerate posts.json for every article category.

Run by .github/workflows/build-index.yml on every push, so adding an
article never requires hand-editing a manifest.

For each category folder that contains `article.html`, this scans the
folder for *.md files (ignoring `_*` templates), reads their YAML-ish
front matter, and writes a sorted posts.json next to them.

Front matter keys used:
    title     article title          (default: first # heading, else filename)
    date      YYYY-MM-DD             (default: "")
    summary   one-line blurb         (default: first paragraph)
    tags      comma separated        (default: [])
    draft     true -> skipped entirely

Everything else in the file is left untouched.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FRONT_MATTER = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?", re.S)


def parse_front_matter(text):
    """Return (dict, remaining body). Missing front matter -> ({}, text)."""
    m = FRONT_MATTER.match(text)
    if not m:
        return {}, text

    data = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key:
            data[key] = value
    return data, text[m.end():]


def first_heading(body):
    m = re.search(r"^\s*#\s+(.+)$", body, re.M)
    return m.group(1).strip() if m else ""


def first_paragraph(body):
    """First run of non-heading, non-blank, non-code text."""
    in_code = False
    for raw in body.splitlines():
        line = raw.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line:
            continue
        if line.startswith("#") or line.startswith("!") or line.startswith("|"):
            continue
        plain = re.sub(r"[*_`\[\]]", "", line)
        plain = re.sub(r"\(.*?\)", "", plain).strip()
        if plain:
            return plain[:180]
    return ""


def build_for(folder):
    """Write folder/posts.json from the *.md files inside it."""
    files = sorted(
        f for f in os.listdir(folder)
        if f.endswith(".md") and not f.startswith("_")
    )

    entries = []
    for name in files:
        path = os.path.join(folder, name)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()

        meta, body = parse_front_matter(text)

        # `draft: true` keeps a file in the repo but off the site.
        if str(meta.get("draft", "")).lower() in ("true", "yes", "1"):
            continue

        title = meta.get("title") or first_heading(body) or name[:-3]
        summary = meta.get("summary") or first_paragraph(body)
        tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]

        entries.append({
            "file": name,
            "title": title,
            "date": meta.get("date", ""),
            "summary": summary,
            "tags": tags,
        })

    # Newest first; undated entries sink to the bottom in filename order.
    entries.sort(key=lambda e: (e["date"], e["file"]), reverse=True)

    out = os.path.join(folder, "posts.json")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(entries, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    return len(entries), out


def main():
    categories = []
    for name in sorted(os.listdir(ROOT)):
        folder = os.path.join(ROOT, name)
        if not os.path.isdir(folder):
            continue
        if name.startswith(".") or name in ("assets", "images", "scripts"):
            continue
        if os.path.exists(os.path.join(folder, "article.html")):
            categories.append(folder)

    if not categories:
        print("no category folders found (expected a folder with article.html)")
        return 1

    total = 0
    for folder in categories:
        count, out = build_for(folder)
        total += count
        print("%-14s %2d posts -> %s" % (os.path.basename(folder), count, out))

    print("\n%d categories, %d posts total" % (len(categories), total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
