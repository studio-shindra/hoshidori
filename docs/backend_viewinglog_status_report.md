# Backend ViewingLog ステータス管理変更 報告書

## 変更日
2026-03-16

## 変更概要
ViewingLog を user × performance で1件のみ持つ設計に変更。
「観る」→「観た」はレコード新規作成ではなく、既存レコードの状態更新として扱う。

## 変更ファイル

### reviews/models.py
- `UniqueConstraint(fields=['user', 'performance'])` を追加
- migration 0004 で適用済み
- 適用前に既存の重複データ（user=1, performance=18）を手動で解消

### reviews/views.py
- `ViewingLogViewSet.create()` をオーバーライド
- POST /api/viewing-logs/ が upsert 動作になった
  - 既存レコードあり → partial update して 200 で返す
  - 既存レコードなし → 新規作成して 201 で返す

### reviews/serializers.py
- planned 時に `watched_time` も null クリアするよう修正

## 動作仕様

| 操作 | 既存レコード | 結果 |
|------|------------|------|
| 「観る」を押す | なし | planned で新規作成 |
| 「観る」を押す | あり（planned/watched） | planned に更新 |
| 「観た」を押す | なし | watched で新規作成 |
| 「観た」を押す | あり（planned） | watched に更新、watched_on 反映 |
| 「観た」を押す | あり（watched） | watched_on 等を更新 |

## フロント側への影響
- フロントは従来通り POST /api/viewing-logs/ を叩くだけ
- backend 側で upsert するため、フロント側の変更は不要
