# daisy-media-app
Daisy用のInstagram・LINE・Webアプリ運用ダッシュボード
## 自動収集と公開ポリシー（最新版）

### 自動収集
- GitHub Actions `Collect event candidates` が毎日候補を自動収集
- 収集元は `data/instagram-sources.json`
- 収集結果は `data/events.json` に `status: 要確認` で反映

### 公開ポリシー
- 公開ページには `status: 公式確認済み` のみ表示
- `要確認` は管理用候補（スマホで確認後に承認）
- 承認時は `status` を `公式確認済み` に変更し、必要なら `verifiedAt` を入力

### 収益導線
- イベントカードに楽天・Amazonの2系統アフィリエイトリンクを表示
- フィールド:
  - `rakutenAffiliateUrl`
  - `amazonAffiliateUrl`
