<script setup>
import { ref, computed } from 'vue'
import { IconSend } from '@tabler/icons-vue'

const name = ref('')
const email = ref('')
const category = ref('general')
const body = ref('')

const categories = [
  { value: 'general', label: '一般的なお問い合わせ' },
  { value: 'delete', label: 'コンテンツ削除依頼' },
  { value: 'report', label: '不適切なコンテンツの通報' },
  { value: 'bug', label: '不具合・バグ報告' },
  { value: 'other', label: 'その他' },
]

const categoryLabel = computed(() => categories.find(c => c.value === category.value)?.label || '')

const mailtoLink = computed(() => {
  const subject = encodeURIComponent(`[HOSHIDORI] ${categoryLabel.value}`)
  const bodyText = encodeURIComponent(
    `お名前: ${name.value}\nメールアドレス: ${email.value}\nカテゴリ: ${categoryLabel.value}\n\n${body.value}`
  )
  return `mailto:info@studio-shindra.com?subject=${subject}&body=${bodyText}`
})

const canSend = computed(() => body.value.trim().length > 0)
</script>

<template>
  <div class="container py-4" style="max-width: 720px;">
    <h1 class="h3 mb-4">お問い合わせ</h1>

    <!-- Contact form -->
    <section class="mb-5">
      <div class="d-flex flex-column gap-3">
        <div>
          <label class="form-label small text-secondary">お名前</label>
          <input v-model="name" type="text" class="form-control bg-dark border-secondary text-light form-control-sm" placeholder="お名前（任意）" />
        </div>
        <div>
          <label class="form-label small text-secondary">メールアドレス</label>
          <input v-model="email" type="email" class="form-control bg-dark border-secondary text-light form-control-sm" placeholder="返信先メールアドレス（任意）" />
        </div>
        <div>
          <label class="form-label small text-secondary">カテゴリ</label>
          <select v-model="category" class="form-select bg-dark border-secondary text-light form-select-sm">
            <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
          </select>
        </div>
        <div>
          <label class="form-label small text-secondary">お問い合わせ内容</label>
          <textarea v-model="body" rows="5" class="form-control bg-dark border-secondary text-light form-control-sm" placeholder="お問い合わせ内容をご記入ください"></textarea>
        </div>
        <a :href="mailtoLink" class="btn btn-primary-rose fw-medium d-flex align-items-center justify-content-center gap-2" :class="{ disabled: !canSend }">
          <IconSend :size="16" />メールで送信
        </a>
        <p class="text-secondary small mb-0">メールアプリが起動します。送信先: info@studio-shindra.com</p>
      </div>
    </section>

    <hr class="border-secondary" />

    <!-- Existing info sections -->
    <section class="mb-4">
      <h2 class="h5">削除依頼について</h2>
      <p>権利侵害やプライバシー侵害等を理由としてコンテンツの削除を依頼される場合は、以下の情報をメールにてお送りください。</p>
      <div class="card bg-dark border-secondary">
        <div class="card-body">
          <ol class="mb-0">
            <li class="mb-2"><strong>対象コンテンツのURL:</strong> 該当する投稿やページのURLをお知らせください。</li>
            <li class="mb-2"><strong>削除を求める理由:</strong> 権利侵害の内容、権利の種類（著作権、肖像権等）など、具体的にご記載ください。</li>
            <li class="mb-2"><strong>権利者であることの説明:</strong> ご自身が権利者である場合、またはその代理人である場合、その旨をご記載ください。</li>
            <li class="mb-2"><strong>ご連絡先:</strong> お名前（または団体名）、メールアドレスをご記載ください。</li>
          </ol>
        </div>
      </div>
    </section>

    <section class="mb-4">
      <h2 class="h5">対応について</h2>
      <ul>
        <li>ご連絡いただいた内容を確認の上、合理的な期間内に対応いたします。</li>
        <li>権利侵害の疑いが認められる場合、該当コンテンツの削除または非公開化を行います。</li>
        <li>内容によっては追加の確認をお願いする場合があります。</li>
      </ul>
    </section>
  </div>
</template>
