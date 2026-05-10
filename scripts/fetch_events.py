#!/usr/bin/env python3
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "events.json"
SOURCES_FILE = ROOT / "data" / "instagram-sources.json"

CATEGORY_AFFILIATE = {
    "イベント": {
        "rakuten": "https://hb.afl.rakuten.co.jp/hgc/EVENT-RKT-EXAMPLE",
        "amazon": "https://amzn.to/EVENT-AMZ-EXAMPLE"
    },
    "カフェ": {
        "rakuten": "https://hb.afl.rakuten.co.jp/hgc/CAFE-RKT-EXAMPLE",
        "amazon": "https://amzn.to/CAFE-AMZ-EXAMPLE"
    },
    "ドッグラン": {
        "rakuten": "https://hb.afl.rakuten.co.jp/hgc/RUN-RKT-EXAMPLE",
        "amazon": "https://amzn.to/RUN-AMZ-EXAMPLE"
    }
}

def load_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def clean_handle(handle: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._]", "", handle.replace("@", "").strip())

def source_candidates():
    src = load_json(SOURCES_FILE, {"policy": {}, "accounts": [], "hashtags": []})
    accounts = src.get("accounts", [])
    hashtags = src.get("hashtags", [])
    out = []

    # アカウント由来候補
    for acc in accounts:
        if not acc.get("enabled", True):
            continue
        handle = clean_handle(str(acc.get("handle", "")))
        category = acc.get("category", "イベント")
        aff = CATEGORY_AFFILIATE.get(category, {"rakuten": "", "amazon": ""})

        out.append({
            "title": f"Instagram候補: {acc.get('displayName', handle or 'unknown')}",
            "category": category,
            "prefecture": acc.get("prefecture", "要確認"),
            "area": acc.get("area", "要確認"),
            "date": "要確認",
            "status": "要確認",
            "summary": "Instagramアカウント由来の候補。公開前に内容確認が必要。",
            "url": f"https://www.instagram.com/{handle}/" if handle else "",
            "sourceType": "candidate",
            "source": "instagram-account",
            "rakutenAffiliateUrl": acc.get("affiliate", {}).get("rakuten", aff["rakuten"]),
            "amazonAffiliateUrl": acc.get("affiliate", {}).get("amazon", aff["amazon"]),
            "imageUrl": acc.get("imageUrl", ""),
            "seasons": acc.get("seasons", ["春", "夏", "秋", "冬"]),
            "largeDogFriendly": bool(acc.get("largeDogFriendly", False)),
            "mapUrl": acc.get("mapUrl", "")
        })

    # ハッシュタグ由来候補（APIなしなのでタグページ候補）
    for h in hashtags:
        if not h.get("enabled", True):
            continue
        tag = str(h.get("tag", "")).replace("#", "").strip()
        if not tag:
            continue
        category = h.get("category", "イベント")
        aff = CATEGORY_AFFILIATE.get(category, {"rakuten": "", "amazon": ""})

        out.append({
            "title": f"ハッシュタグ候補: #{tag}",
            "category": category,
            "prefecture": h.get("prefecture", "要確認"),
            "area": h.get("area", "要確認"),
            "date": "要確認",
            "status": "要確認",
            "summary": f"ハッシュタグ #{tag} 由来の候補。投稿内容を人手確認してください。",
            "url": f"https://www.instagram.com/explore/tags/{tag}/",
            "sourceType": "candidate",
            "source": "instagram-hashtag",
            "rakutenAffiliateUrl": h.get("rakutenAffiliateUrl", aff["rakuten"]),
            "amazonAffiliateUrl": h.get("amazonAffiliateUrl", aff["amazon"]),
            "imageUrl": h.get("imageUrl", ""),
            "seasons": h.get("seasons", ["春", "夏", "秋", "冬"]),
            "largeDogFriendly": bool(h.get("largeDogFriendly", False)),
            "mapUrl": h.get("mapUrl", "")
        })

    return out

def upsert(events, candidates):
    by_key = {(e.get("title"), e.get("date")): e for e in events}
    by_url = {e.get("url"): e for e in events if e.get("url")}
    next_id = max([e.get("id", 0) for e in events] + [0]) + 1
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for c in candidates:
        if c.get("url") and not str(c["url"]).startswith("https://"):
            continue
        key = (c["title"], c["date"])
        ex = by_key.get(key) or (by_url.get(c.get("url")) if c.get("url") else None)

        if ex:
            if ex.get("status") == "要確認":
                ex.update({**c, "updatedAt": now})
            continue

        new_item = {
            "id": next_id,
            "verifiedAt": "",
            "updatedAt": now,
            **c
        }
        events.append(new_item)
        by_key[key] = new_item
        if c.get("url"):
            by_url[c["url"]] = new_item
        next_id += 1

    return sorted(events, key=lambda x: x.get("id", 0))

def main():
    events = load_json(DATA_FILE, [])
    events = upsert(events, source_candidates())
    save_json(DATA_FILE, events)
    print(f"updated: {len(events)} events")

if __name__ == "__main__":
    main()
