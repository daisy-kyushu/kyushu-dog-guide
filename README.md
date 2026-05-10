# Daisy's Kyushu Guide（九州・犬・ガイド）

犬連れで行ける九州のおでかけ情報（イベント / カフェ / キャンプ / ホテル / 山歩き）をまとめるサイトです。

## 方針
- 収集は自動（GitHub Actions）
- 公開は手動承認（スマホ確認）
- `要確認` があればLINE通知（broadcast）

## 必須ファイル
- `data/events.json`
- `data/instagram-sources.json`
- `scripts/fetch_events.py`
- `.github/workflows/collect-events.yml`

## 公開ルール
- 候補は `status: 要確認`
- 公開は `status: 公式確認済み` のみ表示

## LINE通知
- Secret: `LINE_CHANNEL_ACCESS_TOKEN`
- `Collect event candidates` 実行時に `要確認` 件数を通知

## アフィリエイト
- `rakutenAffiliateUrl`（楽天）
- `amazonAffiliateUrl`（Amazon）
- 管理画面URLではなく「実際のアフィリエイトリンク」を保存する

## トラブル時
- workflowエラー時は `collect-events.yml` を再貼り付け
- サイト反映されない時は `Ctrl+F5`
- JSONエラー時は `data/events.json` のカンマ/引用符を確認
