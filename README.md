# Daisy's Kyushu Guide（九州・犬・ガイド）

犬連れで行ける九州のおでかけ情報（イベント / カフェ / キャンプ / ホテル / 山歩き）をまとめるサイトです。  
収集は自動化し、公開は人手確認で品質を担保します。

---

## 公開URL
- https://daisy-kyushu.github.io/kyushu-dog-guide/

---

## このプロジェクトの方針（重要）

### 1) 収集は自動
- GitHub Actions `Collect event candidates` を毎日実行
- `scripts/fetch_events.py` が候補を `data/events.json` に追加/更新

### 2) 公開は手動承認
- 収集直後は `status: 要確認`
- スマホで確認後 `status: 公式確認済み` に変更
- 公開ページには `公式確認済み` のみ表示（誤情報防止）

### 3) 通知はLINE
- `要確認` が1件以上あると LINE に通知
- 通知は broadcast 方式（`LINE_TO_USER_ID` 不要）

---

## ディレクトリ構成

- `index.html` … 画面本体
- `app.js` … 一覧表示・検索・絞り込み
- `styles.css` … スタイル
- `data/events.json` … 掲載データ本体
- `data/instagram-sources.json` … Instagram候補ソース設定
- `scripts/fetch_events.py` … 候補収集スクリプト
- `.github/workflows/collect-events.yml` … 収集 + 通知
- `.github/workflows/deploy-pages.yml` … Pagesデプロイ

---

## データ仕様（events.json）

各要素は以下の形です（代表）:

```json
{
  "id": 1,
  "title": "イベント名",
  "category": "イベント",
  "prefecture": "福岡",
  "area": "福岡市",
  "date": "2026/08/10",
  "status": "要確認",
  "summary": "概要",
  "url": "https://example.com",
  "sourceType": "candidate",
  "source": "instagram-official",
  "rakutenAffiliateUrl": "https://hb.afl.rakuten.co.jp/...",
  "amazonAffiliateUrl": "https://amzn.to/...",
  "imageUrl": "https://example.com/photo.jpg",
  "seasons": ["春", "夏"],
  "largeDogFriendly": true,
  "mapUrl": "https://maps.google.com/?q=...",
  "verifiedAt": "",
  "updatedAt": "2026-05-10T08:00:00Z"
}
