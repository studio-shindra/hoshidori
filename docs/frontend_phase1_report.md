# HOSHIDORI Frontend Phase1 実装レポート

## 概要

Vue 3 + Vite + Pinia で「観劇メモアプリ」のフロントエンドを構築。
最低限の画面・ルーティング・API接続を通し、スマホで触れる状態にした。

## 実装した画面

| 画面 | パス | 説明 |
|---|---|---|
| Home | / | サービストップ、主要導線 |
| Login | /login | ログインフォーム |
| Register | /register | 新規登録フォーム |
| TheatersList | /theaters | 劇場一覧 |
| TheaterDetail | /theaters/:slug | 劇場詳細 + 近くの店 |
| WorksList | /works | 作品一覧 |
| ViewingLogsList | /logs | 観劇メモ一覧（これから観る/観た切替） |
| ViewingLogCreate | /logs/new | 観劇メモ作成 |
| ShopDetail | /shops/:slug | 店舗詳細 + クーポン利用 |
| Dashboard | /dashboard | 店舗ダッシュボード |

## ルーティング一覧

```
/               → HomeView
/login          → LoginView
/register       → RegisterView
/theaters       → TheatersListView
/theaters/:slug → TheaterDetailView
/works          → WorksListView
/logs           → ViewingLogsListView      (要認証)
/logs/new       → ViewingLogCreateView     (要認証)
/shops/:slug    → ShopDetailView
/dashboard      → DashboardView            (要認証)
```

## 認証の流れ

1. 起動時に `App.vue` の `onMounted` で `fetchMe()` を実行
2. cookie/session ベースの認証（`credentials: "include"`）
3. `requiresAuth: true` のルートには `beforeEach` ガードで未ログイン時 `/login` へリダイレクト
4. CSRF トークンは cookie から `csrftoken` を取得して `X-CSRFToken` ヘッダに付与

## API接続一覧

| 画面 | API | メソッド |
|---|---|---|
| 全体 | /api/auth/me/ | GET |
| Login | /api/auth/login/ | POST |
| Register | /api/auth/register/ | POST |
| Home (logout) | /api/auth/logout/ | POST |
| TheatersList | /api/theaters/ | GET |
| TheaterDetail | /api/theaters/{slug}/ | GET |
| TheaterDetail | /api/theaters/{slug}/shops/ | GET |
| WorksList | /api/works/ | GET |
| ViewingLogsList | /api/viewing-logs/?status={} | GET |
| ViewingLogCreate | /api/viewing-logs/ | POST |
| ShopDetail | /api/shops/{slug}/ | GET |
| ShopDetail | /api/shops/{slug}/click/ | POST |
| ShopDetail | /api/coupons/ | GET |
| ShopDetail | /api/coupons/{id}/use/ | POST |
| Dashboard | /api/dashboard/ | GET |

## 変更ファイル一覧

### 新規作成
- `frontend/.env`
- `frontend/src/lib/api.js`
- `frontend/src/stores/auth.js`
- `frontend/src/views/LoginView.vue`
- `frontend/src/views/RegisterView.vue`
- `frontend/src/views/TheatersListView.vue`
- `frontend/src/views/TheaterDetailView.vue`
- `frontend/src/views/WorksListView.vue`
- `frontend/src/views/ViewingLogsListView.vue`
- `frontend/src/views/ViewingLogCreateView.vue`
- `frontend/src/views/ShopDetailView.vue`
- `frontend/src/views/DashboardView.vue`

### 修正
- `frontend/src/main.js`（変更なし、既存構造を利用）
- `frontend/src/App.vue`
- `frontend/src/router/index.js`
- `frontend/src/views/HomeView.vue`
- `frontend/src/assets/main.css`

## 動作確認手順

```bash
cd frontend
npm install
npm run dev
```

ブラウザで http://localhost:5173 を開く。

backend を http://localhost:8000 で起動しておくこと。
CORS 設定が必要な場合は backend の settings.py で以下を確認:

```python
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
CORS_ALLOW_CREDENTIALS = True
```

### 確認項目
1. `/` — ホーム画面が表示される
2. `/login` — ログインできる
3. `/register` — 新規登録できる
4. `/theaters` — 劇場一覧が表示される
5. `/theaters/{slug}` — 劇場詳細と近くの店が表示される
6. `/works` — 作品一覧が表示される
7. `/logs` — 観劇メモが表示される（要ログイン）
8. `/logs/new` — 観劇メモを作成できる（要ログイン）
9. `/shops/{slug}` — 店舗詳細とクーポンが表示される
10. `/dashboard` — 店舗ダッシュボードが表示される（店舗ユーザーのみ）

## Phase2 でやること

- 作品詳細ページ
- 公演選択UI（ViewingLogCreate の改善）
- レビュー投稿 / いいね機能
- プロフィールページ
- 検索・フィルタ機能
- デザイン改善・レスポンシブ対応強化
- エラーハンドリング強化
- ページネーション対応
