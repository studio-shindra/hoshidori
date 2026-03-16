# frontend_header_bootstrap_fix_report

## 変更ファイル
- frontend/src/App.vue

## 変更内容
- header の位置指定を Bootstrap 5 準拠に修正
  - `position-fixed top-0 left-0` -> `fixed-top start-0 end-0`
- ヘッダー内要素の縦中央寄せを安定化
  - header 自体を flex コンテナ化して `d-flex align-items-center` を付与
  - `min-height: 40px` -> `height: 40px` に変更
- ヘッダー内ロゴを親 container 基準で absolute 中央配置に変更
  - `start-0 end-0` 方式を廃止し、`top-50 start-50 translate-middle` を採用
- 固定ヘッダーで本文が隠れないよう main に上余白を追加
  - `main-content` に `pt-5` を付与

## 不具合原因メモ
- Bootstrap 5 では `left-0` がユーティリティとして存在せず、`start-0` を使う必要がある。
- `align-items-center` を子要素側だけに付けても、親要素の高さが確定していないと見た目上中央に揃わないケースがある。
- `start-0 end-0` の absolute 要素は横幅いっぱいになるため、内部要素が意図した中央に見えないことがある。

## 確認ポイント
- 画面上部にヘッダーが固定されること
- ログイン/ユーザー名リンクがヘッダー内で表示されること
- 本文先頭がヘッダーの下に隠れないこと
