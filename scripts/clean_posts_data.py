#!/usr/bin/env python3
"""
Clean posts_data.json by deduplicating entries that share the same canonical link or slug.
Keeps the newest post when duplicates are found (based on parsed date), backs up the original file.

Usage: python3 scripts/clean_posts_data.py
"""
import json
from pathlib import Path
from datetime import datetime
from email.utils import parsedate_to_datetime

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "posts_data.json"
BACKUP_FILE = ROOT / "posts_data.json.bak"


def parse_date(d):
    if not d:
        return None
    if isinstance(d, (int, float)):
        try:
            return datetime.fromtimestamp(d)
        except Exception:
            return None
    if isinstance(d, datetime):
        return d
    # try RFC-style parse first
    try:
        return parsedate_to_datetime(d)
    except Exception:
        pass
    # try ISO
    try:
        return datetime.fromisoformat(d)
    except Exception:
        return None


def key_for(post):
    # Prefer canonical link if present, else slug
    link = post.get("link") or ""
    slug = post.get("slug") or ""
    # normalize by stripping trailing slash
    if link.endswith("/"):
        link = link[:-1]
    return link or slug


def main():
    if not DATA_FILE.exists():
        print(f"No posts_data.json found at {DATA_FILE}")
        return
    data = json.loads(DATA_FILE.read_text())
    print(f"Loaded {len(data)} posts from {DATA_FILE}")

    # backup
    if not BACKUP_FILE.exists():
        BACKUP_FILE.write_text(DATA_FILE.read_text())
        print(f"Backed up original to {BACKUP_FILE}")

    groups = {}
    for p in data:
        k = key_for(p)
        if not k:
            # fallback: use title
            k = p.get("title", "")
        existing = groups.get(k)
        if not existing:
            groups[k] = p
            continue
        # compare dates, prefer newest
        a = parse_date(existing.get("date"))
        b = parse_date(p.get("date"))
        if a is None and b is None:
            # keep existing
            continue
        if a is None:
            groups[k] = p
            continue
        if b is None:
            continue
        if b > a:
            groups[k] = p

    cleaned = list(groups.values())
    print(f"Deduped to {len(cleaned)} unique posts")
    # sort newest-first
    cleaned.sort(key=lambda x: parse_date(x.get("date")) or datetime.min, reverse=True)

    DATA_FILE.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False))
    print(f"Wrote cleaned posts_data.json ({len(cleaned)} posts)")


if __name__ == "__main__":
    main()
