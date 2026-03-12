# HOSHIDORI Backend Phase 1.5 実装レポート

## 概要

Phase1（観劇ログ/レビューアプリ）から Phase1.5（観劇メモアプリ）への思想差分を吸収する最小パッチ。
全面作り直しは行わず、既存コードを活かしたまま差分修正のみを実施。

### 思想変更の核心
1. 「レビューアプリ」→「観劇メモアプリ」への重心移動
2. 「店舗掲載」→「クーポン利用ログ」への初期KPI重心移動（Phase2で対応）

## 変更一覧

### 1. accounts.User — role フィールド追加

| フィールド | 型 | 説明 |
|---|---|---|
| role | CharField(max_length=20) | user / shop / admin の3権限 |

- default='user'（既存ユーザーに影響なし）
- 店舗ユーザー・管理者の区別が初期から可能に

### 2. reviews.ViewingLog — status フィールド追加

| フィールド | 型 | 説明 |
|---|---|---|
| status | CharField(max_length=20) | watched（観た）/ planned（これから観る） |

- default='watched'（既存データとの後方互換）
- watched_on を null=True, blank=True に変更（planned 時は日付不要）
- ordering を `-watched_on` → `-created_at` に変更
- `?status=planned` / `?status=watched` でフィルタ可能
- バリデーション: watched 時は watched_on 必須、planned 時は watched_on を自動クリア
- PATCH 対応: 部分更新時も既存値をフォールバックして整合性を保証

### 3. reviews.Like — 新規モデル

| フィールド | 型 | 説明 |
|---|---|---|
| user | FK(User) | いいねしたユーザー |
| review | FK(Review) | 対象レビュー |
| created_at | DateTimeField | いいね日時 |

- unique_together: [user, review]
- ReviewSerializer に `like_count`, `is_liked` を追加
- N+1対策: `Count`/`Exists` アノテーションで一括取得（一覧APIでクエリ数固定）
- 冪等性: POST(like済み)→200、DELETE(未like)→404（エラーにならない）

### 4. works.Work — is_approved デフォルト変更

- `is_approved` の default を `False` → `True` に変更
- ユーザー自由入力ベースの運用思想に合致
- 暫定データとしてまず公開し、後から名寄せ・統合する運用

### 5. accounts.permissions — IsShopUser 追加

- `role` が `shop` または `admin` のユーザーのみアクセス可能
- Phase2 の店舗ダッシュボードAPI等で使用予定

## API差分

### 変更されたエンドポイント

| Endpoint | 変更内容 |
|---|---|
| GET /api/auth/me/ | レスポンスに `role` 追加 |
| POST /api/auth/register/ | レスポンスに `role` 追加 |
| GET/POST /api/viewing-logs/ | `status` フィールド追加、`watched_on` が任意に |
| GET /api/viewing-logs/?status=planned | ステータスフィルタ追加 |
| GET /api/reviews/ | `like_count`, `is_liked` 追加 |
| GET /api/reviews/{id}/ | `like_count`, `is_liked` 追加 |

### 新規エンドポイント

| Method | Endpoint | 認証 | 説明 |
|---|---|---|---|
| POST | /api/reviews/{id}/like/ | 必要 | いいね追加 |
| DELETE | /api/reviews/{id}/like/ | 必要 | いいね取消 |

## 変更ファイル一覧

### 修正
- `accounts/models.py` — User に role フィールド追加
- `accounts/serializers.py` — UserSerializer に role 追加
- `accounts/permissions.py` — IsShopUser 追加
- `reviews/models.py` — ViewingLog に status 追加 + watched_on nullable化 + Like モデル新規
- `reviews/serializers.py` — ViewingLogSerializer に status 追加 + ReviewSerializer に like_count/is_liked + LikeSerializer 新規
- `reviews/views.py` — ViewingLog に status フィルタ + ReviewViewSet に like アクション追加
- `reviews/admin.py` — ViewingLogAdmin に status 追加 + LikeAdmin 新規
- `works/models.py` — Work.is_approved の default を True に

### 新規
- `docs/backend_phase1.5_report.md` — 本ファイル

## migration 実行方法

```bash
source venv/bin/activate

# マイグレーション作成
python3 manage.py makemigrations accounts reviews works

# マイグレーション実行
python3 manage.py migrate
```

## APIテスト例（curl）

```bash
BASE=http://localhost:8000/api

# 観劇メモ（観た）を記録
curl -X POST $BASE/viewing-logs/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -b cookies.txt \
  -d '{"performance":1,"status":"watched","watched_on":"2026-03-01","memo":"最前列で鑑賞"}'

# これから観る舞台を記録
curl -X POST $BASE/viewing-logs/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -b cookies.txt \
  -d '{"performance":2,"status":"planned","memo":"チケット購入済み"}'

# これから観るリストを取得
curl $BASE/viewing-logs/?status=planned -b cookies.txt

# 観たリストを取得
curl $BASE/viewing-logs/?status=watched -b cookies.txt

# レビューにいいね
curl -X POST $BASE/reviews/1/like/ \
  -H "X-CSRFToken: <token>" \
  -b cookies.txt

# いいね取消
curl -X DELETE $BASE/reviews/1/like/ \
  -H "X-CSRFToken: <token>" \
  -b cookies.txt

# レビュー一覧（like_count, is_liked 付き）
curl $BASE/reviews/ -b cookies.txt
```

## Phase2 でやること

### 新規アプリ: shops
- **Shop** — name, slug, category, description, address, nearest_station, distance_note, website_url, instagram_url, tabelog_url, google_map_url, phone_number, opening_hours_text, benefit_text, is_active, owner(FK User)
- **TheaterShop** — theater(FK), shop(FK), sort_order, is_featured
- **Coupon** — shop(FK), title, description, discount_text, conditions, is_active, start_date, end_date
- **CouponUseLog** — coupon(FK), user(FK), performance(nullable FK), used_at
- **ShopClickLog** — shop(FK), user(nullable FK), source_type, clicked_target
- **ShopPlan** — name, monthly_price, description, is_active
- **ShopSubscription** — shop(FK), plan(FK), status, stripe_customer_id, stripe_subscription_id, current_period_start, current_period_end

### Phase2 API
| Method | Endpoint | 認証 | 説明 |
|---|---|---|---|
| GET | /api/shops/ | 不要 | 店舗一覧 |
| GET | /api/shops/{slug}/ | 不要 | 店舗詳細 |
| GET | /api/shops/{slug}/coupons/ | 不要 | 店舗のクーポン一覧 |
| POST | /api/coupons/{id}/use/ | 必要 | クーポン利用記録 |
| GET | /api/dashboard/ | 店舗ユーザー | 自店舗ダッシュボード |
| POST | /api/shops/{id}/click/ | 不要 | クリック記録 |

### Phase2 優先順
1. Coupon / CouponUseLog（初期KPIの中核）
2. Shop / TheaterShop
3. 店舗ダッシュボードAPI
4. ShopClickLog
5. ShopPlan / ShopSubscription / Stripe（構造のみ先行）
