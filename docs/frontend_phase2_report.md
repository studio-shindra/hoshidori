# HOSHIDORI Frontend Phase 2 報告書

## 概要
既存のPhase1/Phase1.5実装をベースに、確定したUI骨格（ダークテーマ・作品主役・Letterboxd/Filmarks的構造）に寄せる改修を実施。MockViewのデザインを参考に、全画面をダークトーンに統一。アイコンはTabler Iconsを導入。

## 今回整えた画面

### 1. App.vue（シェル）
- ダークテーマ化（背景 #0a0a0b、テキスト #e4e4e7）
- Tabler Icons をボトムナビに導入（IconHome, IconBuildingCommunity, IconMask, IconPencil, IconUser）
- ヘッダー・ボトムナビに backdrop-filter blur 適用
- アクティブリンク色を rose (#f43f5e) に統一

### 2. HomeView.vue（トップページ）
- 件数カード3枚（これから観る / 観た / 感想）をAPI接続で表示
- 「これから観る」セクション：横スクロールカード
- 「最近観た作品」セクション：リストカード
- 未ログイン時：ログイン/新規登録導線
- 空状態のUI表示

### 3. WorkDetailView.vue（作品ページ）★ 主役画面
- ヒーロー画像エリア（画像なし時はプレースホルダー + ポスター投稿導線）
- 作品情報（タイトル、劇団名、劇場名、日付）
- アクションボタン3つ（これから観る / 観た / 感想を書く）
- 記録ページ・ポスター投稿への導線ボタン
- インライン記録フォーム・感想投稿フォーム
- みんなの感想一覧（アバター、タグ、いいね）
- 近くの店セクション（Retty風カード、おすすめバッジ、クーポンボタン）

### 4. ViewingLogCreateView.vue（記録投稿ページ）
- 「記録する」専用ページとして整理
- ステータス切替ボタン（これから観る / 観た）
- メモ / 感想 textarea
- 下書き保存ボタン（見た目のみ）
- 投稿ボタン
- ポスター画像投稿UIは含まない（分離済み）

### 5. PosterUploadView.vue（ポスター投稿ページ）★ 新規
- `/works/:slug/poster` ルートで追加
- 対象作品名表示
- 現在の画像表示エリア
- 画像アップロードエリア（モック）
- 補足文：「この画像は作品ページのトップ画像候補になります」
- 送信ボタン
- API接続は未実装（モック状態）

### 6. TheaterDetailView.vue（劇場ページ）
- 店カードをRetty風に改修
- おすすめバッジ（badge-featured）
- 店写真エリア（プレースホルダー）
- ジャンル・徒歩分数・説明文
- クーポンボタン

### 7. ShopDetailView.vue（店詳細ページ）
- ダークテーマ化
- 特典ボックスをrose系カードに
- リンクボタン群をdarkボタンに
- クーポンセクションのダークテーマ対応

### 8. その他ダークテーマ化
- WorksListView.vue
- TheatersListView.vue
- ViewingLogsListView.vue
- MyPageView.vue
- LoginView.vue
- RegisterView.vue

## 追加した導線
- WorkDetailView → ポスター投稿ページ（`/works/:slug/poster`）
- WorkDetailView → 記録ページ（`/logs/new`）
- HomeView → 作品検索（`/works`）
- ヒーロー画像なし時 → ポスター投稿ページ

## 作品主役UIへの変更点
- 作品ページをヒーロー画像付きの主役画面に
- Letterboxd/Filmarks的な構造（作品→感想→周辺情報）
- 写真のない作品もプレースホルダーで成立するUI
- Instagram型（写真SNS）ではなく「作品 + 記録」のUI

## 記録投稿とポスター投稿の分離
- `/logs/new`：観劇記録専用（ステータス + メモ）
- `/works/:slug/poster`：ポスター画像投稿専用（モック）
- 記録ページにはポスター画像投稿UIを含まない

## 技術変更
- `@tabler/icons-vue` パッケージ追加
- Bootstrap 5 dark theme (`data-bs-theme="dark"`) 活用
- 絵文字アイコン → Tabler SVGアイコンに置換
- カラーパレット統一（amber #f59e0b, green #34d399, rose #f43f5e）

## 変更ファイル一覧
### 修正
- `src/assets/main.css`
- `src/App.vue`
- `src/router/index.js`
- `src/views/HomeView.vue`
- `src/views/WorkDetailView.vue`
- `src/views/ViewingLogCreateView.vue`
- `src/views/TheaterDetailView.vue`
- `src/views/ShopDetailView.vue`
- `src/views/WorksListView.vue`
- `src/views/TheatersListView.vue`
- `src/views/ViewingLogsListView.vue`
- `src/views/MyPageView.vue`
- `src/views/LoginView.vue`
- `src/views/RegisterView.vue`

### 新規
- `src/views/PosterUploadView.vue`

## 動作確認手順
```bash
cd frontend
npm install
npm run dev
```

1. `http://localhost:5173/` → トップページ（ダーク、件数カード）
2. `http://localhost:5173/works` → 作品一覧（ダークカード）
3. `http://localhost:5173/works/{slug}` → 作品詳細（ヒーロー、感想、店）
4. `http://localhost:5173/works/{slug}/poster` → ポスター投稿（モック）
5. `http://localhost:5173/logs/new` → 記録投稿（ダークフォーム）
6. `http://localhost:5173/theaters/{slug}` → 劇場詳細（Retty風店カード）
7. `http://localhost:5173/shops/{slug}` → 店詳細（ダーク）
8. `http://localhost:5173/mypage` → マイページ（統計カード）

## 次フェーズ候補
1. ポスター投稿のAPI接続（画像アップロード実装）
2. 作品画像がある場合の表示対応
3. 作品検索機能（フリーワード / フィルタ）
4. 感想へのタグ機能
5. 下書き保存のAPI接続
6. 店カードの実画像対応
7. プッシュ通知 / お知らせ機能
8. マイページの観劇履歴詳細表示
