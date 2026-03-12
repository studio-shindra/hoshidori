# Frontend Phase 3 実装報告書

## 実施日
2026-03-12

## 概要
Backend Phase 3 に合わせて5機能をフロントエンドに実装。ポスター投稿本実装、作品/公演作成UI、クーポンUX改善、ダッシュボード改善、検索導入。

---

## 1. ポスター投稿本実装

### 変更ファイル
- `src/views/PosterUploadView.vue` — 全面書き換え
- `src/views/WorkDetailView.vue` — ポスター画像表示対応
- `src/lib/api.js` — `upload()` メソッド追加（FormData対応）

### 実装内容
- `/api/works/{slug}/posters/` に接続
- ファイル選択 → プレビュー → キャプション入力 → 送信
- 投稿済みポスター一覧表示（選択中バッジ付き）
- 現在のトップ画像表示（selected_poster の image を表示）

### WorkDetailView の変更
- `selected_poster_image_url` がある場合 → ヒーロー画像として表示
- ない場合 → 「ポスター画像募集中」プレースホルダー（既存動作維持）
- ポスター投稿者クレジット表示: `Top image by @display_name`
- 「ポスターを投稿」導線

---

## 2. 作品作成 / 公演作成UI

### 新規ファイル
- `src/views/WorkCreateView.vue`
- `src/views/PerformanceCreateView.vue`

### 追加ルート
- `/works/new` → WorkCreateView（認証必須）
- `/performances/new` → PerformanceCreateView（認証必須）

### WorkCreateView
- タイトル + 説明（任意）の最小入力
- 作成成功後 → 作品詳細ページへ遷移
- slug は backend で自動生成

### PerformanceCreateView
- 作品選択 + 劇場選択 + 開始日 + 終了日（必須）
- カンパニー名 + メモ（任意）
- 「作品が見つからない場合 →」リンクで WorkCreateView へ

### 導線
- WorksListView に「作品登録」ボタン追加
- WorkDetailView に「公演を追加」ボタン追加

---

## 3. クーポン利用UX改善

### 変更ファイル
- `src/views/ShopDetailView.vue`

### 実装内容
- `/api/shops/{slug}/coupons/` を使用（店舗別クーポン取得）
- クーポンごとに独立したフィードバック表示
- 利用成功時: 緑色で「クーポンを利用しました！ (HH:MM)」
- 429（クールダウン中）: 黄色で「短時間での再利用はできません（残り約N分）」
- discount_text, conditions も表示

---

## 4. 店舗ダッシュボード改善

### 変更ファイル
- `src/views/DashboardView.vue` — 全面書き換え

### 実装内容
- Bootstrap 5 のダークテーマに統一
- 4カードのスタッツグリッド（クーポン利用/クリック × 総数/今日）
- 直近7日のクーポン利用数 → Bootstrap progress バーで横棒グラフ風表示
- 直近10件のクーポン利用履歴リスト（タイトル + 日時）

---

## 5. 検索導入

### 変更ファイル
- `src/views/WorksListView.vue` — 検索フォーム追加
- `src/views/TheatersListView.vue` — 検索フォーム追加
- `src/views/HomeView.vue` — 検索導線追加

### 実装内容
- 作品一覧: テキスト入力 + 検索ボタン → `?q=` で API 呼び出し
- 劇場一覧: 同上
- ホーム: 「作品を検索」「劇場を検索」のクイックリンク
- Enter または検索ボタンで検索実行

---

## 変更ファイル一覧

| ファイル | 変更内容 |
|---------|---------|
| src/lib/api.js | upload() メソッド追加 |
| src/router/index.js | /works/new, /performances/new 追加 |
| src/views/PosterUploadView.vue | ポスター投稿本実装 |
| src/views/WorkDetailView.vue | ポスター画像表示、公演追加導線 |
| src/views/WorkCreateView.vue | 新規作成 |
| src/views/PerformanceCreateView.vue | 新規作成 |
| src/views/ShopDetailView.vue | クーポンUX改善 |
| src/views/DashboardView.vue | 履歴・グラフ追加 |
| src/views/WorksListView.vue | 検索フォーム追加 |
| src/views/TheatersListView.vue | 検索フォーム追加 |
| src/views/HomeView.vue | 検索導線追加 |

---

## 動作確認手順

```bash
cd frontend && npm run dev
```

### 確認ポイント
1. `/works` で作品名検索 → 結果が絞り込まれる
2. `/theaters` で劇場名検索 → 結果が絞り込まれる
3. `/works/new` で作品作成 → slug 自動生成で作品ページへ
4. `/performances/new` で公演追加 → 成功メッセージ
5. `/works/{slug}` でポスター画像表示 or 募集中プレースホルダー
6. `/works/{slug}/poster` で画像アップロード → 投稿成功
7. `/shops/{slug}` でクーポン利用 → 成功/クールダウン表示
8. `/dashboard` でスタッツ + 履歴 + 日別グラフ

---

## 次フェーズへの引き継ぎ事項

- ポスター画像のクライアントサイドリサイズは未実装
- 公演作成時の作品/劇場検索（セレクトが多い場合のUX）は改善余地あり
- ダッシュボードのグラフは progress バーで簡易実装。Chart.js 等の導入は後回し
- 検索は Enter / ボタン実行。リアルタイム検索（debounce）は未実装
