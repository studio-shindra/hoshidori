# Frontend クーポン詳細モーダル 報告書

## 変更日
2026-03-16

## 変更概要
クーポンカードをタップするとチケット風モーダルで詳細を表示する機能を実装。
将来的なQRクーポン拡張に対応できる構造。

## 変更ファイル

### 新規: src/components/CouponDetailModal.vue
- チケット風デザインのモーダルコンポーネント
- props: `coupon`, `shopName`
- emit: `close`, `use`
- 表示内容: タイトル、割引額、説明、利用条件、有効期間
- 「この画面をお店に見せる」ボタン
- 将来拡張: `coupon.display_type === 'qr'` で QR表示エリアが出る構造

### 変更: src/views/ShopDetailView.vue
- クーポン一覧をカード → タップ可能なボタンに変更
- タップで CouponDetailModal を開く
- モーダルの「利用する」で既存の useCoupon() を実行
- 未使用の auth, IconCheck, IconClock を削除

## UI仕様
- クーポンカード: ローズ色の破線ボーダー、右に矢印
- モーダル: チケット風（上下にギザギザ、左右に破線ボーダー）
- 背景タップで閉じる

## 将来拡張
Coupon モデルに `display_type` フィールドを追加すれば:
- `text`: 現在の表示（デフォルト）
- `qr`: QRコード表示
- `image`: 画像クーポン表示
