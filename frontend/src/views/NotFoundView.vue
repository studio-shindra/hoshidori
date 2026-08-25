<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { IconArrowRight } from '@tabler/icons-vue'

const router = useRouter()
const seconds = ref(2)
let redirectTimer
let countdownTimer

onMounted(() => {
  countdownTimer = window.setInterval(() => { seconds.value = Math.max(0, seconds.value - 1) }, 1000)
  redirectTimer = window.setTimeout(() => router.replace('/'), 2200)
})

onBeforeUnmount(() => {
  window.clearInterval(countdownTimer)
  window.clearTimeout(redirectTimer)
})
</script>

<template>
  <section class="not-found text-center">
    <div class="error-code">404</div>
    <h1>ページが見つかりません</h1>
    <p>{{ seconds }}秒後にトップへ戻ります。</p>
    <button class="btn btn-outline-light btn-sm" @click="router.replace('/')">
      今すぐトップへ <IconArrowRight :size="15" />
    </button>
  </section>
</template>

<style scoped>
.not-found { min-height: 58vh; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.error-code { color: #f43f5e; font-size: 4.6rem; font-weight: 900; line-height: 1; letter-spacing: -.08em; text-shadow: 0 0 30px rgba(244,63,94,.25); }
h1 { margin: 1rem 0 .5rem; font-size: 1.1rem; }
p { margin-bottom: 1.5rem; color: #71717a; font-size: .76rem; }
button { display: inline-flex; align-items: center; gap: .35rem; }
</style>
