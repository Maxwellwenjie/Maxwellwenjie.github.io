#!/usr/bin/env python3
"""
build-douban.py — turn a Douban export (xlsx / csv) into data/douban.json.

Built for the 豆伴 (tofu) Chrome extension export, which produces one
workbook with a sheet per data type:

    看过 / 在看 / 想看        movies
    读过 / 在读 / 想读        books
    听过 / 在听 / 想听        music  (ignored by default)
    影评 / 书评 / 广播 / 日记 / 相册 / 关注 / 豆邮 / 豆列 / 留言板
                              skipped — not interest records

Columns in those sheets are: 标题 简介 豆瓣评分 链接 创建时间 我的评分 标签 评论

Two traps this script handles:
  * "豆瓣评分" is the site average, "我的评分" is yours. Only the latter is
    used, otherwise every item would look like it scored ~8/10.
  * Sheet names, not column names, decide whether a row is a movie or a book.

Usage:
    python scripts/build-douban.py 豆伴(12345).xlsx --inspect
    python scripts/build-douban.py 豆伴(12345).xlsx --profile https://www.douban.com/people/12345/
    python scripts/build-douban.py export.xlsx --include-music
"""

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "douban.json")

# (field, exact/partial keywords, reject words)
FIELD_RULES = [
    ("title",     ["标题", "名称", "书名", "片名", "title"], []),
    ("rating",    ["我的评分", "个人评分", "我的打分", "评分", "星级", "rating"], ["豆瓣", "平均"]),
    ("date",      ["标记日期", "标记时间", "打分日期", "创建时间", "日期", "date"], []),
    ("comment",   ["短评", "我的短评", "评论", "comment"], []),
    ("tags",      ["标签", "tag"], []),
    ("year",      ["上映年份", "上映日期", "出版年", "年份", "year"], []),
    ("author",    ["作者", "导演", "author", "director"], []),
    ("publisher", ["出版社", "制片国家", "publisher"], []),
    ("link",      ["链接", "网址", "url", "link"], []),
]

# sheet name -> (kind, status). Checked in order, first regex hit wins.
SHEET_RULES = [
    (r"读过|在读|想读|读书|图书|书籍", "book"),
    (r"看过|在看|想看|电影|影视|剧集|电视", "movie"),
    (r"听过|在听|想听|音乐", "music"),
]

SKIP_SHEETS = ("影评", "书评", "乐评", "剧评", "游戏评论", "广播", "日记",
               "相册", "关注", "黑名单", "豆邮", "豆列", "留言", "笔记")

WORD_RATING = {"力荐": 5, "推荐": 4, "还行": 3, "较差": 2, "很差": 1}
STAR_RE = re.compile(r"[★]+")


def norm_key(s):
    return re.sub(r"[\s_\-()（）\[\]]", "", str(s)).lower()


def match_column(header):
    """Map one header cell to a canonical field name, or None."""
    h = norm_key(header)
    if not h:
        return None
    for field, words, _ in FIELD_RULES:
        for w in words:
            if norm_key(w) == h:
                return field
    for field, words, reject in FIELD_RULES:
        for w in words:
            if norm_key(w) in h and not any(norm_key(r) in h for r in reject):
                return field
    return None


def build_map(header_row):
    mapping = {}
    for idx, cell in enumerate(header_row):
        field = match_column(cell)
        if field and field not in mapping:
            mapping[field] = idx
    return mapping


def clean(v):
    if v is None:
        return ""
    if isinstance(v, (dt.datetime, dt.date)):
        return v.strftime("%Y-%m-%d")
    s = str(v).strip()
    return "" if s.lower() in ("nan", "none", "nat", "无") else s


def parse_rating(v):
    s = clean(v)
    if not s:
        return 0
    for word, score in WORD_RATING.items():
        if word in s:
            return score
    stars = STAR_RE.search(s)
    if stars:
        return min(5, len(stars.group(0)))
    m = re.search(r"(\d+(?:\.\d+)?)", s)
    if m:
        n = float(m.group(1))
        if 0 < n <= 5:
            return int(round(n))
        if 5 < n <= 10:           # a 10-point score slipped through
            return max(1, int(round(n / 2.0)))
    return 0


def parse_date(v):
    s = clean(v)
    if not s:
        return ""
    m = re.search(r"(\d{4})[-/年.](\d{1,2})[-/月.](\d{1,2})", s)
    if m:
        return "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3)))
    m = re.search(r"(\d{4})", s)
    return m.group(1) if m else ""


def parse_year(v):
    m = re.search(r"(19|20)\d{2}", clean(v))
    return int(m.group(0)) if m else None


def parse_tags(v):
    s = clean(v)
    if not s:
        return []
    return [t.strip() for t in re.split(r"[,，/、|;；]", s) if t.strip()][:8]


def classify(name):
    """Return (kind, status) for a sheet name, or (None, None) to skip."""
    n = norm_key(name)
    for hint in SKIP_SHEETS:
        if norm_key(hint) in n:
            return None, None
    kind = None
    for pattern, k in SHEET_RULES:
        if re.search(pattern, n):
            kind = k
            break
    if kind is None:
        return None, None

    if re.search(r"想看|想读|想听", n):
        return kind, "wish"
    if re.search(r"在看|在读|在听", n):
        return kind, "doing"
    return kind, "done"


def rows_to_records(header, rows, kind, status, sheet_name):
    mapping = build_map(header)
    if "title" not in mapping:
        return [], mapping

    is_tv = bool(re.search(r"剧|电视", norm_key(sheet_name)))
    records = []
    for row in rows:
        def get(field):
            idx = mapping.get(field)
            return row[idx] if idx is not None and idx < len(row) else None

        title = clean(get("title"))
        if not title:
            continue

        rec = {
            "title": title,
            "rating": parse_rating(get("rating")),
            "date": parse_date(get("date")),
            "kind": "tv" if (kind == "movie" and is_tv) else kind,
            "status": status,
            "tags": parse_tags(get("tags")),
        }

        comment = clean(get("comment"))
        if comment:
            rec["comment"] = comment[:280]

        year = parse_year(get("year"))
        if year:
            rec["year"] = year

        for field in ("author", "publisher"):
            val = clean(get(field))
            if val:
                rec[field] = val[:80]

        link = clean(get("link"))
        if link.startswith("http"):
            rec["link"] = link

        records.append(rec)

    return records, mapping


def read_xlsx(path):
    from openpyxl import load_workbook

    wb = load_workbook(path, read_only=True, data_only=True)
    out = []
    for ws in wb.worksheets:
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        rows = [r for r in rows if any(clean(c) for c in r)]
        if len(rows) >= 2:
            out.append((ws.title, rows[0], rows[1:]))
    wb.close()
    return out


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = [r for r in csv.reader(fh) if any(clean(c) for c in r)]
    return [(os.path.splitext(os.path.basename(path))[0], rows[0], rows[1:])] \
        if len(rows) >= 2 else []


def read_json_export(path):
    """Records produced by scripts/douban-console.js: {type, user, items[]}."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    items = data.get("items", []) if isinstance(data, dict) else data
    kind = (data.get("type") if isinstance(data, dict) else None) or "movie"
    user = data.get("user", "") if isinstance(data, dict) else ""

    records = []
    for it in items:
        raw = clean(it.get("title"))
        # Movie pages stuff every AKA name into the title attribute:
        #   "玛丽和麦克斯 / Mary and Max\n   / 玛丽和马克思 / 巧克力情缘(台)"
        # Keep the leading title only.
        title = re.split(r"\s+/\s+", raw.replace("\n", " "))[0]
        title = re.sub(r"\s+", " ", title).strip(" /").strip()
        if not title:
            continue
        rec = {
            "title": title,
            "rating": parse_rating(it.get("rating")),
            "date": parse_date(it.get("date")),
            "kind": it.get("kind") or kind,
            "status": "done",
            "tags": [clean(t) for t in (it.get("tags") or []) if clean(t)][:8],
        }
        comment = clean(it.get("comment"))
        if comment:
            rec["comment"] = comment[:280]
        link = clean(it.get("link"))
        if link.startswith("http"):
            rec["link"] = link
        if it.get("year"):
            rec["year"] = int(it["year"])
        else:
            # pub looks like "作者 / 出版社 / 2010" or "导演: X 主演: Y 2014 / 美国"
            m = re.search(r"(19|20)\d{2}", clean(it.get("pub")))
            if m:
                rec["year"] = int(m.group(0))
        records.append(rec)

    return kind, user, records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", help="xlsx or csv export file(s)")
    ap.add_argument("--profile", default="", help="Douban profile URL")
    ap.add_argument("--include-music", action="store_true", help="also keep 听过 records")
    ap.add_argument("--include-wishlist", action="store_true",
                    help="also keep 想看 / 想读")
    ap.add_argument("--inspect", action="store_true",
                    help="print what was detected, write nothing")
    args = ap.parse_args()

    sheets = []
    buckets = {"movie": [], "book": [], "music": []}
    found_user = ""

    for path in args.inputs:
        if not os.path.exists(path):
            print("missing file: %s" % path)
            return 1
        if path.lower().endswith(".json"):
            kind, user, records = read_json_export(path)
            found_user = found_user or user
            print("[ok]   %-14s %3d 条  (console json)" % (os.path.basename(path)[:14], len(records)))
            buckets[kind if kind in buckets else "movie"].extend(records)
            continue
        sheets.extend(read_xlsx(path) if path.lower().endswith((".xlsx", ".xlsm"))
                      else read_csv(path))

    for name, header, rows in sheets:
        kind, status = classify(name)
        if kind is None:
            print("[skip] %-14s 不是书影音记录" % name)
            continue
        if kind == "music" and not args.include_music:
            print("[skip] %-14s 音乐（默认不收）" % name)
            continue
        if status != "done" and not args.include_wishlist:
            print("[skip] %-14s 状态 %s（默认只收 看过/读过）" % (name, status))
            continue

        records, mapping = rows_to_records(header, rows, kind, status, name)
        if not records:
            print("[warn] %-14s 找不到标题列，列名为：%s"
                  % (name, " | ".join(clean(h) for h in header if clean(h))))
            continue
        print("[ok]   %-14s %3d 条  列: %s"
              % (name, len(records), ",".join(sorted(mapping))))
        buckets[kind].extend(records)

    movies, books = buckets["movie"], buckets["book"]

    if args.inspect:
        print("\n--inspect 模式，未写文件：%d 部影视，%d 本书。"
              % (len(movies), len(books)))
        for label, pool in (("movie", movies), ("book", books)):
            for s in pool[:3]:
                print("   %-5s %s" % (label, json.dumps(s, ensure_ascii=False)))
        return 0

    if not movies and not books:
        print("\n没有解析出任何记录。先用 --inspect 看列名是否被识别。")
        return 1

    movies.sort(key=lambda r: (r["date"], r["title"]), reverse=True)
    books.sort(key=lambda r: (r["date"], r["title"]), reverse=True)

    profile_url = args.profile or (
        "https://www.douban.com/people/%s/" % found_user if found_user else "")
    payload = {
        "profile": {"url": profile_url, "synced": dt.date.today().isoformat()},
        "movies": movies,
        "books": books,
    }
    if args.include_music and buckets["music"]:
        payload["music"] = buckets["music"]

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    rated = [r["rating"] for r in movies + books if r["rating"]]
    print("\n%d 部影视 / %d 本书 -> %s" % (len(movies), len(books), OUT))
    if rated:
        print("平均评分 %.2f（基于 %d 条评分）" % (sum(rated) / len(rated), len(rated)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
