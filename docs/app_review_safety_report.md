# App Store審査向け 投稿安全機能 引き継ぎ報告

## 目的

Apple App Review Guideline 1.2のユーザー投稿要件に合わせ、公開される観劇メモへ投稿フィルター・通報・ユーザーブロックを追加した。

## 追加した機能

### 1. 不適切表現の投稿前フィルター

- 公開される観劇メモ本文とプロフィールの表示名・自己紹介をサーバー側で検査する。
- 全角・半角、大小文字、空白や記号による表記揺れを正規化してから判定する。
- 該当時は保存せず、表現を変えるよう画面へエラーを返す。
- 判定語は `config/content_moderation.py` で管理する。

### 2. 投稿の通報

- 作品詳細の各観劇メモ右上に「…」メニューを追加した。
- 「この投稿を通報」から理由と任意の補足を送信できる。
- 同じ投稿への再通報は内容を更新し、管理画面の確認待ちへ戻す。
- 通報はDjango管理画面の「Review reports」で確認・対応状況を管理できる。

### 3. ユーザーブロック

- 投稿の「…」メニューから投稿者をブロックできる。
- ブロックしたユーザーの投稿は、作品詳細とホームの「みんなの感激」から除外される。
- マイページの「ブロック中のユーザー」から一覧確認と解除ができる。

## 主な変更ファイル

- `config/content_moderation.py`
- `reviews/models.py`
- `reviews/serializers.py`
- `reviews/views.py`
- `reviews/urls.py`
- `reviews/admin.py`
- `reviews/migrations/0007_reviewreport_userblock.py`
- `frontend/src/views/WorkDetailView.vue`
- `frontend/src/views/BlockedUsersView.vue`
- `frontend/src/views/MyPageView.vue`
- `frontend/src/views/GuidelinesView.vue`
- `frontend/src/router/index.js`

## 確認結果

- Django system check: 問題なし
- Django API tests: 6件成功
- Migration差分: なし
- Vue production build: 成功
- 390×844のスマホ幅で通報メニュー、通報フォーム、ブロック管理画面を目視確認済み

## 運用

- 通報が届いたらDjango管理画面で投稿本文と補足を確認する。
- 必要に応じて投稿削除、投稿者アカウントの無効化を行い、通報状態を「対応済み」にする。
- 新しい不適切表現の傾向があれば `BLOCKED_PHRASES` を追加する。
