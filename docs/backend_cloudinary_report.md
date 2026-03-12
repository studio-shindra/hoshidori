# Backend Cloudinary対応 報告書

## 概要
PosterSubmission モデルを Cloudinary メタデータ保存方式に拡張。
frontend から Cloudinary に直接アップロードされた画像の情報を DB に保存する構成。

## 変更ファイル

### works/models.py
- PosterSubmission に以下のフィールドを追加:
  - `image_url` (URLField, max_length=500) — Cloudinary の secure_url
  - `image_public_id` (CharField, max_length=300) — Cloudinary の public_id
  - `image_width` (IntegerField, null=True) — 画像幅
  - `image_height` (IntegerField, null=True) — 画像高さ
  - `image_format` (CharField, max_length=20) — 画像形式
- 既存の `image` (ImageField) は blank=True に変更し後方互換を維持

### works/serializers.py
- PosterSubmissionSerializer: 新フィールドを fields に追加
- validate() 追加: image または image_url のいずれかが必須
- WorkSerializer.get_selected_poster_image_url: image_url を優先して返却

### works/views.py
- posters アクションの parser_classes に JSONParser を追加
  - Cloudinary アップロード後は JSON で POST するため

### works/admin.py
- PosterSubmissionAdmin: image_url を list_display に追加
- Cloudinary 関連フィールドを readonly_fields に設定

### works/migrations/0004_postersubmission_cloudinary_fields.py
- 上記フィールドの追加マイグレーション

## API仕様

### POST /api/works/{slug}/posters/
リクエスト (JSON):
```json
{
  "image_url": "https://res.cloudinary.com/xxx/image/upload/v.../hoshidori/posters/xxx.jpg",
  "image_public_id": "hoshidori/posters/xxx",
  "image_width": 1200,
  "image_height": 1600,
  "image_format": "jpg",
  "caption": "キャプション（任意）"
}
```

認証必須。user は backend 側で自動セット。

## 注意事項
- Cloudinary API secret は backend の環境変数にのみ保持（今回は削除API未実装のため未使用）
- 既存の ImageField による投稿との後方互換を維持
- 表示は image_url を優先
