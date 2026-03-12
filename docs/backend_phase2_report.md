# HOSHIDORI Backend Phase 2 実装レポート

## 概要

shops アプリの新規作成。店舗・クーポン・クリックログ・サブスク構造を実装。
初期KPIの中核である「クーポン利用ログ」を最優先で構築。

### KPI構造
```
観劇ログ数 → 店舗クリック数 → クーポン使用数
```
CouponUseLog が事業の心臓。

## モデル一覧

### shops

| モデル | 役割 |
|---|---|
| **Shop** | 店舗マスタ（ReadOnly API） |
| **TheaterShop** | 劇場-店舗紐付け |
| **Coupon** | クーポン |
| **CouponUseLog** | クーポン利用ログ（初期KPI中核） |
| **ShopClickLog** | 店舗クリックログ |
| **ShopPlan** | 料金プランマスタ（構造のみ） |
| **ShopSubscription** | サブスク管理（構造のみ、Stripe未実装） |

### 主要フィールド

**Shop**
- name, slug, category, description
- address, nearest_station, distance_note
- website_url, instagram_url, tabelog_url, google_map_url
- phone_number, opening_hours_text, benefit_text
- owner(FK User, nullable) — 店舗ユーザーとの紐付け
- is_active

**TheaterShop**
- theater(FK), shop(FK), sort_order, is_featured
- unique_together: [theater, shop]

**Coupon**
- shop(FK), title, description, discount_text, conditions
- start_date, end_date, is_active

**CouponUseLog**
- coupon(FK), user(FK), performance(nullable FK), used_at

**ShopClickLog**
- shop(FK), user(nullable FK), source_type, clicked_target

**ShopPlan**
- name, monthly_price, description, is_active

**ShopSubscription**
- shop(FK), plan(FK), status
- stripe_customer_id, stripe_subscription_id（構造のみ）
- current_period_start, current_period_end

## API一覧

| Method | Endpoint | 認証 | 説明 |
|---|---|---|---|
| GET | /api/shops/ | 不要 | 店舗一覧（is_active=True のみ） |
| GET | /api/shops/{slug}/ | 不要 | 店舗詳細 |
| POST | /api/shops/{slug}/click/ | 不要 | クリック記録 |
| GET | /api/coupons/ | 不要 | クーポン一覧（is_active=True のみ） |
| GET | /api/coupons/{id}/ | 不要 | クーポン詳細 |
| POST | /api/coupons/{id}/use/ | 必要 | クーポン利用記録 |

## 変更ファイル一覧

### 新規作成
- `shops/models.py` — 全7モデル
- `shops/serializers.py` — Shop, Coupon, CouponUseLog
- `shops/views.py` — ShopViewSet, CouponViewSet
- `shops/urls.py` — router 登録
- `shops/admin.py` — 全モデル admin 登録
- `docs/backend_phase2_report.md` — 本ファイル

### 修正
- `config/settings.py` — INSTALLED_APPS に shops 追加
- `config/urls.py` — api/ に shops.urls 追加

## migration 実行方法

```bash
source venv/bin/activate

# マイグレーション作成
python3 manage.py makemigrations shops

# マイグレーション実行
python3 manage.py migrate
```

## APIテスト例（curl）

```bash
BASE=http://localhost:8000/api

# 店舗一覧
curl $BASE/shops/

# 店舗詳細
curl $BASE/shops/cafe-shimokita/

# 店舗クリック記録
curl -X POST $BASE/shops/cafe-shimokita/click/ \
  -H "Content-Type: application/json" \
  -d '{"source_type":"theater_detail","clicked_target":"website"}'

# クーポン一覧
curl $BASE/coupons/

# クーポン利用
curl -X POST $BASE/coupons/1/use/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -b cookies.txt \
  -d '{"performance":1}'
```

## 設計方針

### 今回実装したもの
- Shop / Coupon の ReadOnly API
- CouponUseLog（POST）— KPIの心臓
- ShopClickLog（POST）— 導線分析用
- ShopPlan / ShopSubscription — 構造のみ（Stripe Webhook 未実装）

### 意図的に実装しなかったもの
- Stripe Webhook 連携（構造だけ先に持ち、実運用は後）
- 店舗ダッシュボードAPI（Phase2.5で対応）
- TheaterDetail に紐づく Shop 一覧（Phase2.5で対応）

## Phase2.5 でやること

### 劇場ページに店舗を出すAPI
- `GET /api/theaters/{slug}/shops/` — 劇場に紐づく店舗一覧（TheaterShop 経由）
- Theater 詳細レスポンスに nearby_shops を nested で返す案も検討

### 店舗ダッシュボードAPI
- `GET /api/dashboard/` — IsShopUser 権限
- 自店舗のクーポン利用数、クリック数、期間集計
- 最小構成: クーポン利用数の日別集計のみ

### 優先順
1. 劇場-店舗連携API（UXの要）
2. 店舗ダッシュボード（店舗営業の要）
3. Stripe サブスク連携（収益化の要）
