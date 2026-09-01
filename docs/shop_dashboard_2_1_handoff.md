# 店舗ダッシュボード 2.1 引き継ぎ

更新日: 2026-08-31

## 対象

- 作業ブランチ: `feature/shop-dashboard-2.1`
- アプリ表示バージョン: `2.1.0`
- 2.0.9 の公開待ちビルドおよび本番環境には未反映
- DBマイグレーションなし
- 新しい外部ライブラリなし

## 実装した内容

### 無料掲載申請

- `/shops/for-business` にPC・スマホ対応の店舗向け申請画面を追加
- Google Placesから店舗名、住所、カテゴリー、Google Maps URL、Place IDを補完
- 近くの劇場を複数選択し、`TheaterShop`へ保存
- 申請直後は `Shop.is_active=False` のため公開されない
- 申請者のアカウントは店舗ロールになり、審査中のダッシュボードを確認できる
- 同じGoogle Place IDの重複申請を拒否
- 1アカウントにつき1店舗

### 運営承認

Django管理画面の店舗一覧に以下の操作を追加した。

- 「選択した申請を無料掲載として承認」
- 「選択した店舗をおすすめ店にする」
- 「選択した店舗を無料掲載に戻す」

無料承認では `is_active=True, is_featured=False` となる。選択済み劇場の周辺店として、Google Mapsの周辺候補より上に表示される。

### 店舗ダッシュボード

- `/dashboard`
- 掲載状態: 審査中 / 無料掲載中 / おすすめ店
- 店舗情報編集
- JPEG / PNG / WebP、8MB以下の店舗画像アップロード
- 累計・今月の「その後行った店」数
- 店舗ページのクリック数、作品別送客、直近7日
- PCは2カラム、スマホは1カラム

### 月額プラン

- プラン名: ホシドリおすすめ店
- 料金: 月額5,000円
- Stripe Checkoutのホスト画面へ遷移
- Stripe Customer Portalで支払い情報・解約を管理
- Webhookで契約状態を同期し、`active` / `trialing` の間だけ `Shop.is_featured=True`
- `invoice.payment_failed` ではおすすめ表示を停止
- カード番号はホシドリ側で保持しない

## 追加したAPI

- `GET/POST /api/shop-application/`
- `GET /api/shop-place-candidates/?q=...`
- `GET/PATCH /api/dashboard/`
- `POST /api/dashboard/image/`
- `POST /api/dashboard/checkout/`
- `POST /api/dashboard/billing-portal/`
- `POST /api/stripe/webhook/`

## Stripe設定

本番・確認環境それぞれに以下を設定する。

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_SHOP_PRICE_ID`: JPY 5,000、月次のPrice ID
- `FRONTEND_URL`: Checkout完了後に戻すフロントURL

Webhook URLは次の形式。

`https://<backend-host>/api/stripe/webhook/`

購読するイベント:

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_failed`

Stripe Customer Portalでは、支払い方法の更新、請求履歴、解約を有効にする。解約は現在の請求期間末で終了する設定を想定している。

## TestFlightまでの安全な出し方

2.0.9はWebViewで本番サイトを参照するため、本番Netlifyを先に上書きすると2.0.9にも新画面が見える。次の順番を推奨する。

1. 2.1確認用バックエンドを用意し、上記Stripeテストキーを設定
2. 2.1確認用フロントを別URLへデプロイ
3. フロントの `VITE_API_BASE_URL` を確認用バックエンドへ向ける
4. EASビルド時の `EXPO_PUBLIC_HOSHIDORI_URL` を確認用フロントURLへ向ける
5. 2.1.0をTestFlightへアップロード
6. 無料申請 → 管理画面承認 → Stripeテスト決済 → 解約まで確認
7. 公開判断後に本番キー・本番URLへ切り替える

`mobile/App.tsx` は `EXPO_PUBLIC_HOSHIDORI_URL` を読むよう変更済み。未指定時は従来どおり `https://hoshidori.netlify.app` を使う。

## 公開前に必要な運営情報

`/commerce` に「特定商取引法に基づく表記」を追加済み。現時点の運営情報として、販売事業者はスタジオシンドラ、運営責任者は小柳 心、問い合わせ先は `info@studio-shindra.com` を表示している。住所・電話番号は請求時に遅滞なく開示する表記とした。月額5,000円、Stripe決済、1か月ごとの自動更新、提供時期、解約と返金条件も掲載済み。対象取引への適用範囲は必要に応じて専門家にも確認する。

参考:

- [消費者庁・通信販売広告について](https://www.no-trouble.caa.go.jp/what/mailorder/advertising.html)
- [消費者庁・通信販売広告Q&A](https://www.no-trouble.caa.go.jp/qa/advertising.html)

利用規約とプライバシーポリシーには、店舗掲載、月額自動更新、Stripe決済、店舗情報の取扱いを追記済み。

## 店舗向けWeb導線

- `/shops/for-business` は未ログインでも料金と仕組みを読める公開ページ
- 申請開始時にアカウント作成またはログインへ進む
- 申請、店舗情報編集、レポート、Stripe申込・解約はすべてWebで完結
- iOSアプリ内の店舗掲載・店舗ダッシュボードへのリンクはSafariで開く
- アプリ内には決済画面を持たない

## 認定店の表示順

認定店一覧は `Shop.featured_order` の小さい順で表示する。2026年9月1日の本番設定は、燗味処を1、il Legameを2として燗味処を先頭にする。

## 確認結果

- Django全テスト: 27件成功
- Django system check: 問題なし
- マイグレーション差分: なし
- Vue本番ビルド: 成功
- React Native TypeScript: 成功
- Expo公開設定: 2.1.0として読込成功
- PC表示（1365×900）: 確認済み
- スマホ表示（390×844）: 確認済み
- Google Placesの店舗候補: 実データで自動入力確認済み
- 劇場検索・複数選択: 確認済み
- 店舗向け公開ページ: 未ログイン表示をブラウザで確認済み
- 特定商取引法に基づく表記: ブラウザで確認済み

## 現時点の未実施

- 本番・確認環境へのデプロイ
- Stripeの商品・Price作成
- Stripe Customer Portal設定
- Stripe Webhook登録
- Stripeテストキーを使った申込・解約の実接続確認
- TestFlightビルド
- App Store審査提出

審査提出はTestFlight確認後の別判断とする。
