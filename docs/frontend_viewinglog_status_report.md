# Frontend ViewingLog ステータス管理変更 報告書

## 変更日
2026-03-16

## 変更概要
backend 側が upsert 化されたため、フロント側のコード変更は不要。
既存の POST /api/viewing-logs/ 呼び出しがそのまま正しく動作する。

## 動作確認

### WorkDetailView
- 「観る」ボタン → POST status=planned → 既存あれば更新
- 「観た」ボタン → POST status=watched → 既存あれば更新
- 同一作品で「観る」→「観た」の順で押しても重複レコードは作られない

### ViewingLogCreateView (/logs/new)
- 同上。POST が upsert として動作

### MyPageView
- 「観る」タブと「観た」タブに同一作品が重複表示されることはない
- 編集・削除は既存の PATCH/DELETE でそのまま動作

### HomeView
- statカードの件数も正確（重複がないため）

## フロント側の変更ファイル
なし（backend の upsert 化で対応完了）
