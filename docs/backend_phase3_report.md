# Backend Phase 3 実装報告書

## 実施日
2026-03-12

## 概要
5つの機能をまとめて実装。作品ポスター投稿、作品/公演作成改善、クーポンUX補助API、ダッシュボード改善、検索API。

---

## 1. 作品ポスター投稿 (PosterSubmission)

### 追加モデル
- `PosterSubmission` (works/models.py)
  - work (FK→Work), user (FK→User), image (ImageField), caption, is_selected, created_at
  - is_selected=True は同一作品で1件のみ（save時に自動排他）

### API
- `GET /api/works/{slug}/posters/` — 作品のポスター一覧
- `POST /api/works/{slug}/posters/` — ポスター投稿（認証必須、multipart/form-data）

### WorkSerializer に追加されたフィールド
- `selected_poster_image_url` — 選択されたポスター画像URL
- `selected_poster_user_display_name` — 投稿者表示名

### Admin
- PosterSubmissionAdmin で is_selected の切り替え可能

### Migration
- `works/migrations/0003_alter_person_slug_alter_work_slug_postersubmission.py`

---

## 2. 作品作成 / 公演作成の受け皿整備

### 変更内容
- Work.slug を `blank=True` に変更 → 未入力で作成可能
- Person.slug も同様に `blank=True` に変更
- モデルの `save()` で slug 未設定時に自動生成
  - `slugify(title, allow_unicode=True)` で日本語タイトル対応
  - 同一 slug が存在する場合は `-2`, `-3`... の suffix を付与
  - タイトルが空 or slug 生成不可の場合は UUID ベースの slug を生成
- WorkSerializer, PersonSerializer で `slug` を `required=False` に設定
- `created_by` は `perform_create` で自動セット（既存動作維持）

---

## 3. クーポン利用UXの補助API

### 追加API
- `GET /api/shops/{slug}/coupons/` — 店舗別クーポン一覧（is_active=True のみ）

### CouponUseLog レスポンス改善
- 利用成功時 (201):
  - `coupon_title`, `used_at`, `cooldown_minutes_remaining` を返却
- クールダウン中 (429):
  - `message`, `cooldown_minutes_remaining`（分単位、小数1桁）を返却

---

## 4. 店舗ダッシュボード改善

### GET /api/dashboard/ の追加レスポンス
- `recent_coupon_uses` — 直近10件のクーポン利用履歴
  - id, coupon_title, used_at, performance_id (nullable)
- `daily_coupon_use_counts` — 直近7日間の日別クーポン利用数
  - date, count（利用がない日は count=0）

### 既存レスポンス（維持）
- shop_id, shop_name, coupon_use_total, coupon_use_today, click_total, click_today

---

## 5. 最低限の検索API

### 追加パラメータ
- `GET /api/works/?q=検索語` — 作品タイトル部分一致検索（大小文字不問）
- `GET /api/theaters/?q=検索語` — 劇場名部分一致検索（大小文字不問）

### 実装方法
- ViewSet の `get_queryset()` で `icontains` フィルタ
- 全文検索エンジン不要、シンプルな LIKE 検索

---

## 変更ファイル一覧

| ファイル | 変更内容 |
|---------|---------|
| works/models.py | PosterSubmission追加、slug blank=True、save()でslug自動生成 |
| works/serializers.py | PosterSubmissionSerializer追加、WorkSerializerにポスター情報、slug required=False |
| works/views.py | posters アクション追加、検索q対応 |
| works/admin.py | PosterSubmissionAdmin追加 |
| works/migrations/0003_... | PosterSubmission作成、slug変更 |
| shops/views.py | shops/{slug}/coupons/ 追加、coupon use レスポンス改善 |
| shops/dashboard_views.py | recent_coupon_uses、daily_coupon_use_counts 追加 |
| shops/urls.py | 変更なし（router経由で自動反映） |
| theaters/views.py | 検索q対応 |
| config/settings.py | MEDIA_URL, MEDIA_ROOT 追加 |
| config/urls.py | DEBUG時のMEDIA配信追加 |

---

## 動作確認コマンド

```bash
python3 manage.py runserver
```

### ポスター投稿
```bash
curl -X POST http://localhost:8000/api/works/{slug}/posters/ \
  -H "Cookie: sessionid=..." \
  -F "image=@poster.jpg" \
  -F "caption=テストポスター"
```

### 作品作成（slug省略）
```bash
curl -X POST http://localhost:8000/api/works/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  -d '{"title": "新しい作品"}'
```

### 店舗別クーポン
```bash
curl http://localhost:8000/api/shops/{slug}/coupons/
```

### ダッシュボード
```bash
curl http://localhost:8000/api/dashboard/ -H "Cookie: sessionid=..."
```

### 検索
```bash
curl "http://localhost:8000/api/works/?q=ハムレット"
curl "http://localhost:8000/api/theaters/?q=帝国"
```

---

## 次フェーズへの引き継ぎ事項

- ポスター画像の最適化（リサイズ、圧縮）は未実装
- ポスター投稿の権限制御は最小限（認証ユーザーなら誰でも投稿可）
- Stripe 連携は未着手
- 検索は icontains のみ。大規模データ時は全文検索エンジン検討
- MEDIA ファイルの本番配信設定（S3等）は未実装
