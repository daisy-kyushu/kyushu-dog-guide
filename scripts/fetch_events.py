#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS_FILE = ROOT / "data" / "events.json"
SOURCES_FILE = ROOT / "data" / "instagram-sources.json"

CATEGORY_DEFAULTS = {
    "イベント": {"rakuten": "", "amazon": ""},
    "カフェ": {"rakuten": "", "amazon": ""},
    "ドッグラン": {"rakuten": "", "amazon": ""},
}

def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def build_hashtag_candidate(tag_obj):
    tag = str(tag_obj.get("tag", "")).replace("#", "").strip()
    if not tag:
        return None

    category = tag_obj.get("category", "イベント")
    aff = CATEGORY_DEFAULTS.get(category, {"rakuten": "", "amazon": ""})

    return {
        "title": f"ハッシュタグ候補: #{tag}",
        "category": category,
        "prefecture": tag_obj.get("prefecture", "要確認"),
        "area": tag_obj.get("area", "要確認"),
        "date": "要確認",
        "status": "要確認",
        "summary": f"Instagramハッシュタグ #{tag} 由来の候補。公開前に確認してください。",
        "url": f"https://www.instagram.com/explore/tags/{tag}/",
        "sourceType": "candidate",
        "source": "instagram-hashtag",
        "rakutenAffiliateUrl": tag_obj.get("rakutenAffiliateUrl", aff["rakuten"]),
        "amazonAffiliateUrl": tag_obj.get("amazonAffiliateUrl", aff["amazon"]),
        "imageUrl": tag_obj.get("imageUrl", ""),
        "seasons": tag_obj.get("seasons", ["春", "夏", "秋", "冬"]),
        "largeDogFriendly": bool(tag_obj.get("largeDogFriendly", False)),
        "mapUrl": tag_obj.get("mapUrl", ""),
    }

def upsert(events, candidates):
    by_key = {(e.get("title"), e.get("date")): e for e in events}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    next_id = max([e.get("id", 0) for e in events] + [0]) + 1

    for c in candidates:
        if not c:
            continue
        key = (c["title"], c["date"])
        existing = by_key.get(key)

        if existing:
            if existing.get("status") == "要確認":
                existing.update({**c, "updatedAt": now})
            continue

        item = {
            "id": next_id,
            "verifiedAt": "",
            "updatedAt": now,
            **c
        }
        events.append(item)
        by_key[key] = item
        next_id += 1

    return sorted(events, key=lambda x: x.get("id", 0))

def main():
    events = load_json(EVENTS_FILE, [])
    src = load_json(SOURCES_FILE, {"hashtags": []})

    hashtags = src.get("hashtags", [])
    candidates = [build_hashtag_candidate(h) for h in hashtags if h.get("enabled", True)]

    events = upsert(events, candidates)
    save_json(EVENTS_FILE, events)
    print(f"updated: {len(events)} events")

if __name__ == "__main__":
    main()
