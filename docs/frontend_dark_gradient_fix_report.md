# frontend_dark_gradient_fix_report

## 変更ファイル
- frontend/src/assets/style/_utilities.scss

## 変更内容
- `.dark-gradient` の背景を以下へ修正
  - 変更前: `linear-gradient(135deg, black, $body-bg-dark)`
  - 変更後: `linear-gradient(to bottom, transparent, $body-bg-dark)`

## 意図
- 要望どおり「上から透明 -> body-bg-dark」へ遷移する見た目に合わせるため。

## 影響範囲
- `.dark-gradient` クラスを使用している箇所の背景見た目のみ。
- 機能ロジックへの影響なし。
