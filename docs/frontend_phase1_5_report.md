# HOSHIDORI Frontend Phase1.5 実装レポート

## 概要

Phase1 の画面に「作品詳細」「感想投稿」「いいね」「マイページ」を追加。
作品 → 公演 → 観劇メモ → 感想 → いいね の一連の導線が通った。

## 追加した画面

| 画面 | パス | 説明 |
|---|---|---|
| WorkDetail | /works/:slug | 作品詳細・公演一覧・感想一覧・観劇メモ登録・感想投稿 |
| MyPage | /mypage | 自分の記録数・感想一覧・ログアウト |

## 改善した画面

| 画面 | 内容 |
|---|---|
| WorksList | 作品名クリックで詳細へ遷移 |
| ViewingLogCreate | 公演をセレクトで選択可能に（手入力廃止） |
| App.vue（ナビ） | マイページ導線追加、ナビ順序改善 |

## ルーティング追加

```
/works/:slug → WorkDetailView
/mypage      → MyPageView (要認証)
```

## 作品 → 公演 → 観劇メモ → 感想 → いいね の流れ

1. `/works` で作品一覧を表示
2. 作品をタップ → `/works/:slug` で作品詳細
3. 作品詳細で公演一覧を確認
4. 「これから観る」「観たを記録」ボタンで観劇メモを即登録
5. 「感想を書く」ボタンで感想投稿フォームを開き投稿
6. みんなの感想一覧で他ユーザーの感想を閲覧
7. ♥ ボタンでいいね / いいね取消
8. `/mypage` で自分の記録数・感想を確認

## API接続追加

| 画面 | API | メソッド |
|---|---|---|
| WorkDetail | /api/works/{slug}/ | GET |
| WorkDetail | /api/performances/ | GET |
| WorkDetail | /api/reviews/ | GET |
| WorkDetail | /api/viewing-logs/ | POST |
| WorkDetail | /api/reviews/ | POST |
| WorkDetail | /api/reviews/{id}/like/ | POST |
| WorkDetail | /api/reviews/{id}/like/ | DELETE |
| ViewingLogCreate | /api/performances/ | GET |
| MyPage | /api/viewing-logs/?status=planned | GET |
| MyPage | /api/viewing-logs/?status=watched | GET |
| MyPage | /api/reviews/ | GET |
| MyPage | /api/auth/logout/ | POST |

## 変更ファイル一覧

### 新規
- `frontend/src/views/WorkDetailView.vue`
- `frontend/src/views/MyPageView.vue`
- `docs/frontend_phase1_5_report.md`

### 修正
- `frontend/src/router/index.js` — /works/:slug, /mypage 追加
- `frontend/src/views/WorksListView.vue` — 詳細リンク追加
- `frontend/src/views/ViewingLogCreateView.vue` — 公演セレクト化
- `frontend/src/App.vue` — ナビにマイページ追加

## 動作確認手順

```bash
cd frontend
npm run dev
```

### 確認項目
1. `/works` — 作品一覧、作品名タップで詳細へ
2. `/works/{slug}` — 作品詳細・公演一覧・みんなの感想表示
3. 作品詳細で「これから観る」「観たを記録」→ 観劇メモ保存
4. 作品詳細で「感想を書く」→ 感想投稿
5. 感想の ♥ でいいね / 取消
6. `/logs/new` — 公演をセレクトで選べる
7. `/mypage` — 記録数・自分の感想・ログアウト
8. ボトムナビにマイページが表示される（ログイン時）

## 次フェーズ候補

- プロフィール編集
- 検索・フィルタ（作品、劇場）
- ページネーション
- レビュー詳細・返信
- 公演カレンダー表示
- デザイン改善
- OGP / シェア機能
