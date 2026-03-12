# HOSHIDORI Backend Phase 1 実装レポート

## 実装したアプリ

| アプリ | 役割 |
|---|---|
| accounts | カスタムUser、認証API（register/login/logout/me） |
| theaters | 劇場マスタ（ReadOnly API） |
| works | 作品・公演・出演者・キャスト |
| reviews | レビュー・観劇ログ |

## モデル一覧

### accounts
- **User** (AbstractUser) — display_name 追加

### theaters
- **Theater** — name, slug, area_name, address, nearest_station, description, website_url, image, is_active

### works
- **Work** — title, slug, description, created_by, is_approved
- **Person** — name, slug, phonetic, profile_text, sns_url, created_by, is_approved
- **Performance** — work(FK), theater(FK), company_name, start_date, end_date, note, created_by, is_approved
- **PerformanceCast** — performance(FK), person(FK), role_name / unique_together: [performance, person]

### reviews
- **Review** — user(FK), performance(FK), title, body, rating_overall(1-5), is_spoiler
- **ViewingLog** — user(FK), performance(FK), watched_on, memo

## API一覧

| Method | Endpoint | 認証 | 説明 |
|---|---|---|---|
| POST | /api/auth/register/ | 不要 | ユーザー登録 |
| POST | /api/auth/login/ | 不要 | ログイン |
| POST | /api/auth/logout/ | 必要 | ログアウト |
| GET | /api/auth/me/ | 必要 | 自分の情報取得 |
| GET | /api/theaters/ | 不要 | 劇場一覧 |
| GET | /api/theaters/{slug}/ | 不要 | 劇場詳細 |
| GET | /api/works/ | 不要 | 作品一覧 |
| POST | /api/works/ | 必要 | 作品作成 |
| GET | /api/works/{slug}/ | 不要 | 作品詳細 |
| GET | /api/performances/ | 不要 | 公演一覧 |
| POST | /api/performances/ | 必要 | 公演作成 |
| GET | /api/performances/{id}/ | 不要 | 公演詳細 |
| GET | /api/people/ | 不要 | 出演者一覧 |
| POST | /api/people/ | 必要 | 出演者作成 |
| GET | /api/people/{slug}/ | 不要 | 出演者詳細 |
| GET | /api/reviews/ | 不要 | レビュー一覧 |
| POST | /api/reviews/ | 必要 | レビュー作成 |
| GET/PUT/PATCH/DELETE | /api/reviews/{id}/ | 必要(所有者) | レビュー編集/削除 |
| GET | /api/viewing-logs/ | 必要 | 自分の観劇ログ一覧 |
| POST | /api/viewing-logs/ | 必要 | 観劇ログ作成 |
| GET/PUT/PATCH/DELETE | /api/viewing-logs/{id}/ | 必要 | 観劇ログ編集/削除 |

## 変更ファイル一覧

### 修正
- `requirements.txt` — djangorestframework, django-cors-headers, Pillow 追加
- `config/settings.py` — 全面書き換え（DRF, CORS, AUTH_USER_MODEL, DB設定等）
- `config/urls.py` — api/ ルーティング追加

### 新規作成
- `accounts/` — models.py, serializers.py, views.py, urls.py, admin.py, permissions.py
- `theaters/` — models.py, serializers.py, views.py, urls.py, admin.py
- `works/` — models.py, serializers.py, views.py, urls.py, admin.py
- `reviews/` — models.py, serializers.py, views.py, urls.py, admin.py
- `docs/backend_phase1_report.md` — 本ファイル

## migration 実行方法

```bash
# 仮想環境の有効化
source venv/bin/activate

# マイグレーション作成（初回のみ）
python3 manage.py makemigrations accounts theaters works reviews

# マイグレーション実行
python3 manage.py migrate

# 管理ユーザー作成
python3 manage.py createsuperuser

# 開発サーバー起動
python3 manage.py runserver
```

## APIテスト例（curl）

```bash
BASE=http://localhost:8000/api

# ユーザー登録
curl -X POST $BASE/auth/register/ \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123","password_confirm":"testpass123"}'

# ログイン
curl -X POST $BASE/auth/login/ \
  -H "Content-Type: application/json" \
  -b cookies.txt -c cookies.txt \
  -d '{"username":"testuser","password":"testpass123"}'

# 自分の情報取得
curl $BASE/auth/me/ -b cookies.txt

# 劇場一覧
curl $BASE/theaters/

# 作品作成
curl -X POST $BASE/works/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $(curl -s -c - $BASE/auth/me/ -b cookies.txt | grep csrftoken | awk '{print $NF}')" \
  -b cookies.txt \
  -d '{"title":"ハムレット","slug":"hamlet","description":"シェイクスピアの悲劇"}'

# レビュー作成（performance IDは実際の値に置換）
curl -X POST $BASE/reviews/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -b cookies.txt \
  -d '{"performance":1,"body":"素晴らしい公演でした","rating_overall":5}'

# 観劇ログ作成
curl -X POST $BASE/viewing-logs/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -b cookies.txt \
  -d '{"performance":1,"watched_on":"2026-03-01","memo":"最前列で鑑賞"}'

# ログアウト
curl -X POST $BASE/auth/logout/ -b cookies.txt
```

## 次フェーズ（Phase 2: shops）でやること

### 新規アプリ: shops
- **Shop** — name, slug, category, description, address, nearest_station, distance_note, website_url, instagram_url, tabelog_url, google_map_url, phone_number, opening_hours_text, benefit_text, is_active
- **TheaterShop** — theater(FK), shop(FK), sort_order, is_featured
- **ShopPlan** — name, monthly_price, description, is_active
- **ShopSubscription** — shop(FK), plan(FK), status, stripe_customer_id, stripe_subscription_id, current_period_start, current_period_end, cancel_at_period_end, started_at, ended_at
- **ShopClickLog** — shop(FK), user(nullable FK), source_type, clicked_target

### API
- `/api/shops/` — 店舗一覧（ReadOnly）
- `/api/shops/{slug}/` — 店舗詳細（ReadOnly）
- `/api/shops/{id}/click/` — クリック記録（AllowAny）
- `/api/admin/shop-subscriptions/` — 管理用CRUD（IsAdminUser）

### その他
- Stripe フィールドはモデルに定義のみ（Webhook実装は後回し）
- Theater詳細で紐づくShop一覧をnestedで返す
