<template>
  <div class="container py-4" style="max-width: 720px;">
    <h1 class="h3 mb-4">プライバシーポリシー</h1>
    <p class="text-muted small mb-4">最終更新日: 2026年8月31日</p>

    <section class="mb-4">
      <h2 class="h5">1. はじめに</h2>
      <p>HOSHIDORI（以下「本サービス」）は、ユーザーの個人情報の保護を重要と考え、個人情報の保護に関する法律その他関連法令を遵守します。本ポリシーは、本サービスにおける個人情報の取り扱いについて説明するものです。</p>
    </section>

    <section class="mb-4">
      <h2 class="h5">2. 取得する情報</h2>
      <p>本サービスでは、以下の情報を取得することがあります。</p>
      <ul>
        <li><strong>アカウント情報:</strong> ユーザー名、メールアドレス、表示名</li>
        <li><strong>投稿コンテンツ:</strong> 観劇記録、感想テキスト、コメント</li>
        <li><strong>投稿画像:</strong> 観劇記録にユーザーがアップロードした写真</li>
        <li><strong>観劇後の店舗記録:</strong> 観劇後に行った店舗と観劇記録との関連情報</li>
        <li><strong>店舗掲載情報:</strong> 店舗名、所在地、連絡先、営業時間、店舗画像、店舗アカウント情報</li>
        <li><strong>決済関連情報:</strong> 契約プラン、決済状況、Stripeが発行する顧客・契約識別子（カード番号は本サービスでは保持しません）</li>
        <li><strong>アクセスログ:</strong> IPアドレス、ブラウザ情報、アクセス日時、ページ閲覧履歴等</li>
      </ul>
    </section>

    <section class="mb-4">
      <h2 class="h5">3. 利用目的</h2>
      <p>取得した情報は、以下の目的で利用します。</p>
      <ul>
        <li>本サービスの提供・運営・改善</li>
        <li>ユーザーへの案内・通知</li>
        <li>不正利用の防止・対応</li>
        <li>利用状況の分析・統計（個人を特定しない形での集計を含む）</li>
        <li>お問い合わせへの対応</li>
        <li>店舗掲載申請の確認、有料掲載プランの提供および請求管理</li>
      </ul>
      <p class="small text-muted">劇場周辺の店舗検索にはGoogle Maps Platformを利用する場合があります。検索時には劇場名・所在地がGoogleへ送信されます。Googleによる情報の取扱いは、<a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Googleプライバシーポリシー</a>をご確認ください。</p>
      <p class="small text-muted">有料掲載プランの決済にはStripeを利用します。決済に必要な情報はStripeへ送信され、Stripeのプライバシーポリシーに基づいて取り扱われます。</p>
    </section>

    <section class="mb-4">
      <h2 class="h5">4. 第三者への提供</h2>
      <p>運営は、以下の場合を除き、ユーザーの個人情報を第三者に提供しません。</p>
      <ul>
        <li>ユーザー本人の同意がある場合</li>
        <li>法令に基づく場合</li>
        <li>人の生命、身体または財産の保護のために必要であり、本人の同意を得ることが困難な場合</li>
        <li>サービス運営に必要な範囲で業務委託先に提供する場合（適切な管理を求めます）</li>
      </ul>
    </section>

    <section class="mb-4">
      <h2 class="h5">5. 情報の管理</h2>
      <p>運営は、取得した個人情報について、適切な安全管理措置を講じ、不正アクセス・漏洩・改ざん・紛失等の防止に努めます。</p>
    </section>

    <section class="mb-4">
      <h2 class="h5">6. 開示・訂正・削除の請求</h2>
      <p>ユーザーは、自己の個人情報について、開示・訂正・利用停止・削除を請求することができます。請求はお問い合わせ窓口までご連絡ください。本人確認を行った上で、合理的な範囲で対応いたします。</p>
    </section>

    <section class="mb-4">
      <h2 class="h5">7. ポリシーの変更</h2>
      <p>本ポリシーは、法令の改正やサービスの変更に伴い、予告なく改定することがあります。改定後のポリシーは本サービス上に掲載した時点で効力を生じます。</p>
    </section>

    <div class="mt-5 pt-3 border-top">
      <p class="text-muted small">個人情報に関するお問い合わせは、<router-link to="/contact">お問い合わせ・削除依頼</router-link>ページよりご連絡ください。</p>
    </div>
  </div>
</template>
