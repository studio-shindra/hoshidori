<template>
  <div class="commerce-page">
    <header class="page-heading">
      <span>LEGAL</span>
      <h1>特定商取引法に基づく表記</h1>
      <p>店舗掲載者向け有料プランについて、以下のとおり表示します。</p>
    </header>

    <dl class="commerce-list">
      <div><dt>販売事業者</dt><dd>スタジオシンドラ</dd></div>
      <div><dt>運営責任者</dt><dd>小柳 心</dd></div>
      <div><dt>所在地</dt><dd>請求があった場合、遅滞なく開示いたします。<RouterLink to="/contact?category=shop">お問い合わせ窓口</RouterLink>よりご請求ください。</dd></div>
      <div><dt>電話番号</dt><dd>請求があった場合、遅滞なく開示いたします。<RouterLink to="/contact?category=shop">お問い合わせ窓口</RouterLink>よりご請求ください。</dd></div>
      <div><dt>メールアドレス</dt><dd><a href="mailto:info@studio-shindra.com">info@studio-shindra.com</a></dd></div>
      <div><dt>販売価格</dt><dd>ホシドリおすすめ店：月額5,000円（税込）</dd></div>
      <div><dt>販売価格以外に必要な費用</dt><dd>本サービスの利用に必要なインターネット接続料金および通信料金は、利用者の負担となります。</dd></div>
      <div><dt>支払方法</dt><dd>クレジットカード決済（Stripe）</dd></div>
      <div><dt>支払時期</dt><dd>初回申込時に決済し、以後は初回決済日を基準として1か月ごとに自動決済します。</dd></div>
      <div><dt>サービスの提供時期</dt><dd>決済完了後、システムへの反映が完了次第、おすすめ店としての優先掲載を開始します。</dd></div>
      <div><dt>契約期間と自動更新</dt><dd>契約期間は1か月です。利用者が解約手続きを行わない限り、同一条件で1か月ごとに自動更新されます。</dd></div>
      <div><dt>解約について</dt><dd>次回決済日の前までに、店舗ダッシュボードの「支払い情報を管理」から解約できます。解約後は支払済みの利用期間末まで利用でき、期間途中の日割り返金は行いません。</dd></div>
      <div><dt>返品・返金について</dt><dd>デジタルサービスの性質上、提供開始後の返品は受け付けていません。法令上必要な場合、または当方の責めに帰すべき事由がある場合を除き、支払済み料金の返金は行いません。</dd></div>
      <div><dt>動作環境</dt><dd>インターネットに接続できる環境と、最新版の主要なWebブラウザが必要です。</dd></div>
    </dl>

    <p class="updated">最終更新日：2026年8月31日</p>
    <RouterLink to="/shops/for-business" class="return-link">店舗掲載について見る →</RouterLink>
  </div>
</template>

<style scoped>
.commerce-page { max-width: 820px; margin: 0 auto; padding: 42px 0 64px; }
.page-heading { margin-bottom: 34px; }
.page-heading span { color: #fb7185; font-size: .65rem; font-weight: 900; letter-spacing: .16em; }
.page-heading h1 { margin: 9px 0 10px; font-size: clamp(1.65rem, 4vw, 2.7rem); font-weight: 900; letter-spacing: -.03em; }
.page-heading p { margin: 0; color: #a1a1aa; font-size: .78rem; }
.commerce-list { overflow: hidden; margin: 0; border: 1px solid rgba(255,255,255,.1); border-radius: 16px; background: #151517; }
.commerce-list > div { display: grid; grid-template-columns: minmax(150px, 30%) 1fr; border-bottom: 1px solid rgba(255,255,255,.08); }
.commerce-list > div:last-child { border-bottom: 0; }
.commerce-list dt, .commerce-list dd { margin: 0; padding: 18px 20px; font-size: .75rem; line-height: 1.8; }
.commerce-list dt { color: #a1a1aa; background: rgba(255,255,255,.025); font-weight: 700; }
.commerce-list dd { color: #e4e4e7; }
.commerce-list a { color: #fda4af; }
.updated { margin: 18px 0 0; color: #52525b; font-size: .65rem; }
.return-link { display: inline-block; margin-top: 24px; color: #fda4af; font-size: .72rem; text-decoration: none; }
@media (max-width: 620px) {
  .commerce-page { padding: 28px 0 48px; }
  .commerce-list > div { grid-template-columns: 1fr; }
  .commerce-list dt { padding-bottom: 4px; background: transparent; color: #71717a; }
  .commerce-list dd { padding-top: 2px; }
}
</style>
