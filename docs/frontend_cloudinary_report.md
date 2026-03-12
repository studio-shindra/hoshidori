# Frontend Cloudinary対応 報告書

## 概要
ポスター画像アップロードを Cloudinary 直接アップロード方式に変更。
API secret を frontend に露出させず、unsigned upload preset を使用。

## 変更ファイル

### frontend/src/views/PosterUploadView.vue
- アップロードフローを2段階に変更:
  1. Cloudinary に直接 POST (`https://api.cloudinary.com/v1_1/{cloud_name}/image/upload`)
  2. 成功後、backend に Cloudinary メタデータを JSON で POST
- フロント側バリデーション追加:
  - 画像ファイルのみ許可 (`file.type.startsWith('image/')`)
  - 10MB サイズ制限
  - 送信前プレビュー表示
- アップロード中の進捗メッセージ表示
- 既存の ImageField データとの互換表示 (`posterImageSrc()` ヘルパー)

### frontend/.env
- `VITE_CLOUDINARY_CLOUD_NAME` 追加
- `VITE_CLOUDINARY_UPLOAD_PRESET` 追加

## 環境変数

| 変数名 | 説明 | 例 |
|--------|------|-----|
| VITE_CLOUDINARY_CLOUD_NAME | Cloudinary cloud name | mycloud |
| VITE_CLOUDINARY_UPLOAD_PRESET | unsigned upload preset 名 | hoshidori_unsigned |

## セキュリティ
- frontend には cloud_name と upload_preset のみ配置
- API key / API secret は一切 frontend に含まない
- unsigned upload preset を使用するため、Cloudinary 側で制限設定が必要

## WorkDetailView.vue
- 変更なし（backend の WorkSerializer が image_url を優先返却するため）
