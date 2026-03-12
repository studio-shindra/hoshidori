# HOSHIDORI Backend Phase 2.5 実装レポート

## 概要

Phase2（shops アプリ）に対して、UX導線・店舗分析・不正防止を追加。
これにより ユーザー導線・店舗導線・分析導線 が全てつながった。

### 導線の完成形
```
ユーザー: 観劇ログ → 劇場ページ → 近くの店 → クーポン使用
店舗:     ダッシュボード → クーポン利用数 / クリック数 確認
```

## 変更一覧

### 1. Theater → Shop API（劇場ページに店舗を出す）

| Method | Endpoint | 認証 | 説明 |
|---|---|---|---|
| GET | /api/theaters/{slug}/shops/ | 不要 | 劇場に紐づく店舗一覧 |

- TheaterShop 経由で `sort_order` 順に取得
- `is_active=True` の店舗のみ

### 2. Shop Dashboard API（店舗ユーザー向け）

| Method | Endpoint | 認証 | 説明 |
|---|---|---|---|
| GET | /api/dashboard/ | IsShopUser | 自店舗のダッシュボード |

レスポンス:
```json
{
  "shop_id": 1,
  "shop_name": "Cafe Shimokita",
  "coupon_use_total": 53,
  "coupon_use_today": 4,
  "click_total": 120,
  "click_today": 9
}
```

- `role` が `shop` または `admin` のユーザーのみアクセス可能
- `Shop.owner` が自分のショップを自動取得
- 店舗未登録の場合は 404

### 3. CouponUseLog 5分重複防止

- 同一ユーザー × 同一クーポン × 5分以内 → 429 で拒否
- 簡易的な不正防止（QR/位置情報不要）

## 変更ファイル一覧

### 修正
- `theaters/views.py` — TheaterViewSet に `shops` アクション追加
- `shops/views.py` — CouponViewSet.use に5分重複チェック追加
- `shops/urls.py` — dashboard エンドポイント追加

### 新規
- `shops/dashboard_views.py` — ShopDashboardView
- `docs/backend_phase2.5_report.md` — 本ファイル

## APIテスト例（curl）

```bash
BASE=http://localhost:8000/api

# 劇場に紐づく店舗一覧
curl $BASE/theaters/honda-gekijo/shops/

# クーポン利用（5分以内の重複は429）
curl -X POST $BASE/coupons/1/use/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -b cookies.txt \
  -d '{"performance":1}'

# 店舗ダッシュボード（shop/admin ユーザーのみ）
curl $BASE/dashboard/ -b cookies.txt
```

## migration

Phase2.5 ではモデル変更なし。migration 不要。

## 全API一覧（Phase2.5 時点）

### accounts
| Method | Endpoint | 認証 | 説明 |
|---|---|---|---|
| POST | /api/auth/register/ | 不要 | ユーザー登録 |
| POST | /api/auth/login/ | 不要 | ログイン |
| POST | /api/auth/logout/ | 必要 | ログアウト |
| GET | /api/auth/me/ | 必要 | 自分の情報取得 |

### theaters
| Method | Endpoint | 認証 | 説明 |
|---|---|---|---|
| GET | /api/theaters/ | 不要 | 劇場一覧 |
| GET | /api/theaters/{slug}/ | 不要 | 劇場詳細 |
| GET | /api/theaters/{slug}/shops/ | 不要 | 劇場に紐づく店舗一覧 |

### works
| Method | Endpoint | 認証 | 説明 |
|---|---|---|---|
| GET | /api/works/ | 不要 | 作品一覧 |
| POST | /api/works/ | 必要 | 作品作成 |
| GET | /api/works/{slug}/ | 不要 | 作品詳細 |
| GET | /api/performances/ | 不要 | 公演一覧 |
| POST | /api/performances/ | 必要 | 公演作成 |
| GET | /api/performances/{id}/ | 不要 | 公演詳細 |
| GET | /api/people/ | 不要 | 出演者一覧 |
| POST | /api/people/ | 必要 | 出演者作成 |
| GET | /api/people/{slug}/ | 不要 | 出演者詳細 |

### reviews
| Method | Endpoint | 認証 | 説明 |
|---|---|---|---|
| GET | /api/reviews/ | 不要 | レビュー一覧（like_count, is_liked付き） |
| POST | /api/reviews/ | 必要 | レビュー作成 |
| GET/PUT/PATCH/DELETE | /api/reviews/{id}/ | 必要(所有者) | レビュー編集/削除 |
| POST | /api/reviews/{id}/like/ | 必要 | いいね追加 |
| DELETE | /api/reviews/{id}/like/ | 必要 | いいね取消 |
| GET | /api/viewing-logs/ | 必要 | 観劇メモ一覧 |
| GET | /api/viewing-logs/?status=planned | 必要 | これから観るリスト |
| GET | /api/viewing-logs/?status=watched | 必要 | 観たリスト |
| POST | /api/viewing-logs/ | 必要 | 観劇メモ作成 |
| GET/PUT/PATCH/DELETE | /api/viewing-logs/{id}/ | 必要 | 観劇メモ編集/削除 |

### shops
| Method | Endpoint | 認証 | 説明 |
|---|---|---|---|
| GET | /api/shops/ | 不要 | 店舗一覧 |
| GET | /api/shops/{slug}/ | 不要 | 店舗詳細 |
| POST | /api/shops/{slug}/click/ | 不要 | クリック記録 |
| GET | /api/coupons/ | 不要 | クーポン一覧 |
| GET | /api/coupons/{id}/ | 不要 | クーポン詳細 |
| POST | /api/coupons/{id}/use/ | 必要 | クーポン利用（5分重複防止） |
| GET | /api/dashboard/ | 店舗ユーザー | 店舗ダッシュボード |

## Phase3 でやること

### Stripe サブスク連携
- Stripe Checkout Session 作成API
- Webhook 受信（subscription.created / updated / deleted）
- ShopSubscription ステータス自動更新
- 掲載課金の有効/無効制御
