#!/usr/bin/env python3
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "データ" / "events.json"
INSTAGRAM_SOURCES_FILE = ROOT / "データ" / "instagram-sources.json"

CANDIDATES = [
    {
        "title": "候補: 九州ドッグイベント",
        "category": "イベント",
        "prefecture": "福岡",
        "area": "未確定",
        "date": "要確認",
        "summary": "自動収集候補。公開前に人手確認が必要。",
        "url": "",
        "sourceType": "candidate",
        "source": "web+instagram",
    }
]

def load_instagram_sources():
    if not INSTAGRAM_SOURCES_FILE.exists():
        return {"policy": {}, "accounts": []}
    return json.loads(INSTAGRAM_SOURCES_FILE.read_text(encoding="utf-8"))

def sources_to_candidates():
    sources = load_instagram_sources()
    policy = sources.get("policy", {})
    keywords = {str(k).strip().lower() for k in policy.get("require_profile_keywords", [])}
    candidates = []

    for acc in sources.get("accounts", []):
        if not acc.get("enabled", False):
            continue

        profile_check = str(acc.get("profileCheck", "")).strip().lower()
        if policy.get("official_only", True) and profile_check not in keywords:
            continue

        handle = str(acc.get("handle", "")).strip()
        handle = re.sub(r"[^a-zA-Z0-9._]", "", handle.replace("@", ""))

        candidates.append({
            "title": f"Instagram候補: {str(acc.get('displayName', acc.get('handle', 'unknown'))).strip()}",
            "category": acc.get("category", "イベント"),
            "prefecture": "要確認",
            "area": "要確認",
            "date": "要確認",
            "summary": "Instagram公式アカウント由来の候補。公開前に内容確認が必要。",
            "url": f"https://www.instagram.com/{handle}/" if handle else "",
            "sourceType": "candidate",
            "source": "instagram-official",
        })

    return candidates

def load_events():
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))

def save_events(events):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")

def upsert_candidates(events):
    existing_by_key = {(e.get("title"), e.get("date")): e for e in events}
    existing_by_url = {e.get("url"): e for e in events if e.get("url")}
    next_id = max([e.get("id", 0) for e in events] + [0]) + 1
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    all_candidates = CANDIDATES + sources_to_candidates()

    for c in all_candidates:
        if c.get("url") and not str(c["url"]).startswith("https://"):
            continue

        key = (c["title"], c["date"])
        existing = existing_by_key.get(key) or (existing_by_url.get(c.get("url")) if c.get("url") else None)

        if existing:
            if existing.get("status") == "要確認":
                existing.update({**c, "updatedAt": now_iso})
            continue

        new_event = {
            "id": next_id,
            "status": "要確認",
            "verifiedAt": "",
            "updatedAt": now_iso,
            **c,
        }
        events.append(new_event)
        existing_by_key[key] = new_event
        if c.get("url"):
            existing_by_url[c["url"]] = new_event
        next_id += 1

    return sorted(events, key=lambda x: x.get("id", 0))

if __name__ == "__main__":
    events = load_events()
    events = upsert_candidates(events)
    save_events(events)
    print(f"updated: {len(events)} events")
