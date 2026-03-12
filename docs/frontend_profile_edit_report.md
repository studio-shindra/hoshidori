# Frontend プロフィール編集 実装報告書

## 実施日
2026-03-12

## 概要
プロフィール編集ページの新規追加。backend に bio フィールドと PATCH /api/auth/me/ を最小追加。

---

## 変更ファイル

| ファイル | 内容 |
|---------|------|
| accounts/models.py | User に bio フィールド追加 |
| accounts/serializers.py | UserSerializer に bio 追加、書き込み可能に変更 |
| accounts/views.py | MeView に PATCH メソッド追加 |
| accounts/migrations/0003_add_bio_to_user.py | migration |
| src/views/ProfileEditView.vue | 新規作成 |
| src/views/MyPageView.vue | 編集ボタン・bio表示追加 |
| src/router/index.js | /mypage/edit ルート追加 |

---

## Backend 変更（最小限）

### User モデル
- `bio`: TextField（blank=True, default=''）

### PATCH /api/auth/me/
- 更新可能: display_name, email, bio
- read_only: id, username, role, date_joined

---

## Frontend

### プロフィール編集ページ (`/mypage/edit`)
- 現在のプロフィール表示（イニシャルアバター + 名前）
- 表示名入力（100文字制限、カウンター付き）
- 自己紹介入力（500文字制限、カウンター付き）
- 保存 → auth store を更新 → マイページへ遷移
- キャンセル → マイページへ戻る

### MyPageView 変更
- ヘッダーに「編集」ボタン追加
- bio がある場合に表示

---

## 確認手順

```bash
# migration 適用
python3 manage.py migrate

# frontend 起動
cd frontend && npm run dev
```

1. ログイン状態で `/mypage` → 「編集」ボタンが表示される
2. `/mypage/edit` → 現在の display_name が入力欄に表示される
3. 表示名・自己紹介を変更 →「保存する」→ マイページに戻り更新が反映
4. マイページに bio が表示される

---

## 次フェーズ候補
- アバター画像アップロード対応（User モデルに avatar フィールド追加）
- パスワード変更
- メールアドレス変更（確認フロー付き）
- アカウント削除
