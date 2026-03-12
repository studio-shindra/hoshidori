# Backend Phase 4 実装報告書

## 実施日
2026-03-12

## 概要
CSVインポート用 management command 群の追加と、サンプルデータCSVの作成。

---

## 1. CSVインポートコマンド

### 追加ファイル
- `theaters/management/commands/import_theaters.py`
- `shops/management/commands/import_shops.py`
- `works/management/commands/import_works.py`
- `works/management/commands/import_performances.py`

### 共通仕様
- UTF-8 の CSV を読み込み
- `--dry-run` オプション対応（実際には保存しない）
- 既存データは slug ベースで update_or_create
- 失敗時は行番号付きエラー表示
- 必須列不足時は明確なエラーメッセージ

### CSVフォーマット

#### theaters.csv
| 列名 | 必須 | 説明 |
|------|------|------|
| name | ○ | 劇場名 |
| slug | ○ | スラッグ（一意） |
| area_name | | エリア名 |
| address | | 住所 |
| nearest_station | | 最寄り駅 |
| description | | 説明 |
| website_url | | Webサイト |
| is_active | | 有効フラグ（デフォルト: true） |

#### shops.csv
| 列名 | 必須 | 説明 |
|------|------|------|
| name | ○ | 店舗名 |
| slug | ○ | スラッグ（一意） |
| category | | カテゴリ |
| description | | 説明 |
| address | | 住所 |
| nearest_station | | 最寄り駅 |
| distance_note | | 距離メモ |
| website_url | | Webサイト |
| instagram_url | | Instagram |
| tabelog_url | | 食べログ |
| google_map_url | | Google Map |
| phone_number | | 電話番号 |
| opening_hours_text | | 営業時間 |
| benefit_text | | 特典テキスト |
| is_active | | 有効フラグ |
| owner_username | | オーナーユーザー名 |
| theater_slug | | 紐付け劇場slug |
| sort_order | | 表示順 |
| is_featured | | おすすめフラグ |

#### works.csv
| 列名 | 必須 | 説明 |
|------|------|------|
| title | ○ | 作品タイトル |
| slug | | スラッグ（省略時は自動生成） |
| description | | 説明 |

#### performances.csv
| 列名 | 必須 | 説明 |
|------|------|------|
| work_slug | ○ | 作品slug |
| theater_slug | ○ | 劇場slug |
| start_date | ○ | 開始日（YYYY-MM-DD） |
| end_date | ○ | 終了日（YYYY-MM-DD） |
| company_name | | カンパニー名 |
| note | | メモ |

---

## 2. サンプルデータ

### ファイル
- `data/theaters_sample.csv` — 劇場5件（下北沢の実在劇場ベース）
- `data/shops_sample.csv` — 店舗5件（劇場紐付けあり）
- `data/works_sample.csv` — 作品5件
- `data/performances_sample.csv` — 公演5件

---

## 3. サンプルデータ投入手順

```bash
# dry-run で確認
python3 manage.py import_theaters data/theaters_sample.csv --dry-run
python3 manage.py import_shops data/shops_sample.csv --dry-run
python3 manage.py import_works data/works_sample.csv --dry-run
python3 manage.py import_performances data/performances_sample.csv --dry-run

# 本投入（順序に注意: 劇場・作品 → 店舗・公演）
python3 manage.py import_theaters data/theaters_sample.csv
python3 manage.py import_works data/works_sample.csv
python3 manage.py import_shops data/shops_sample.csv
python3 manage.py import_performances data/performances_sample.csv
```

---

## 次フェーズ候補
- Django admin からの CSV インポート UI
- 画像の一括インポート対応
- Person（出演者）の CSV インポート
- Coupon の CSV インポート
