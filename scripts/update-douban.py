#!/usr/bin/env python3
"""
update-douban.py — refresh data/douban.json after you mark new things on Douban.

The browser script (scripts/douban-console.js) always re-downloads your
complete list, not just new items, so there is no incremental logic to
worry about: grab everything, rebuild, push.

Workflow
    1. movie page  https://movie.douban.com/people/ID/collect  -> run console script
       (downloads douban-movie-*.json AND douban-tv-*.json)
    2. book page   https://book.douban.com/people/ID/collect   -> run console script
       (downloads douban-book-*.json)
    3. python scripts/update-douban.py --push

This script picks the newest file of each type from your Downloads folder,
rebuilds the data file, and optionally commits and pushes.

Usage:
    python scripts/update-douban.py                 # rebuild only
    python scripts/update-douban.py --push          # rebuild + commit + push
    python scripts/update-douban.py --dir D:/tmp    # look elsewhere for the json
    python scripts/update-douban.py a.json b.json c.json
"""

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "scripts" / "build-douban.py"
OUT = ROOT / "data" / "douban.json"

TYPES = {
    "movie": "douban-movie-*.json",
    "tv": "douban-tv-*.json",
    "book": "douban-book-*.json",
}
REQUIRED = ("movie", "book")


def newest_per_type(folder):
    found = {}
    for kind, pattern in TYPES.items():
        hits = sorted(folder.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        if hits:
            found[kind] = hits[0]
    return found


def age_days(path):
    return (dt.datetime.now() - dt.datetime.fromtimestamp(path.stat().st_mtime)).days


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="explicit json files (overrides auto-detect)")
    ap.add_argument("--dir", default=str(Path.home() / "Downloads"),
                    help="folder to scan for douban-*.json (default: Downloads)")
    ap.add_argument("--push", action="store_true", help="git add/commit/push afterwards")
    args = ap.parse_args()

    if args.files:
        files = [Path(f) for f in args.files]
        missing = [f for f in files if not f.exists()]
        if missing:
            print("找不到文件：" + ", ".join(str(m) for m in missing))
            return 1
    else:
        folder = Path(args.dir)
        if not folder.is_dir():
            print("目录不存在：%s" % folder)
            return 1
        found = newest_per_type(folder)
        missing = [k for k in REQUIRED if k not in found]
        if missing:
            print("缺少这些类型的导出文件：%s" % ", ".join(missing))
            print("请先在对应的豆瓣页面跑一遍 scripts/douban-console.js：")
            if "movie" in missing:
                print("  电影 + 剧集  https://movie.douban.com/people/你的ID/collect")
            if "book" in missing:
                print("  书籍        https://book.douban.com/people/你的ID/collect")
            return 1
        if "tv" not in found:
            print("提示：没有找到剧集导出文件，本次只更新电影和书籍。")

        print("使用的文件（按修改时间取最新）：")
        for kind, path in found.items():
            print("  %-6s %-42s %d 天前" % (kind, path.name, age_days(path)))
        files = [found[k] for k in ("movie", "tv", "book") if k in found]

    print()
    sys.stdout.flush()
    rc = subprocess.call([sys.executable, str(BUILD)] + [str(f) for f in files])
    if rc != 0:
        print("\n构建失败，未做任何提交。")
        return rc

    data = json.loads(OUT.read_text(encoding="utf-8"))
    movies, books = data.get("movies", []), data.get("books", [])
    rated = [r["rating"] for r in movies + books if r.get("rating")]
    print("\n站点数据：%d 部影视 / %d 本书" % (len(movies), len(books)))
    if rated:
        print("平均评分 %.2f（%d 条评分）" % (sum(rated) / len(rated), len(rated)))

    if not args.push:
        print("\n下一步：确认无误后执行")
        print("  git add data/douban.json && git commit -m \"chore: 更新豆瓣数据\" && git push")
        print("或者直接加 --push 让本脚本完成。")
        return 0

    print("\n提交并推送…")
    cmds = [
        ["git", "add", "data/douban.json"],
        ["git", "commit", "-m", "chore: 更新豆瓣书影音数据"],
        ["git", "push", "origin", "master"],
    ]
    for cmd in cmds:
        r = subprocess.call(cmd, cwd=str(ROOT))
        if r != 0:
            if cmd[1] == "commit":
                print("没有可提交的改动（数据未变化）。")
                return 0
            print("命令失败：%s" % " ".join(cmd))
            return r
    print("已推送。约 1 分钟后线上生效。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
