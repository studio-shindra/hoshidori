<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  src: { type: String, required: true },
  alt: { type: String, default: '' },
  aspectRatio: { type: String, default: '3 / 4' },
  rounded: { type: Boolean, default: true },
})

const loaded = ref(false)
const error = ref(false)
const imgRef = ref(null)

function handleLoad() {
  loaded.value = true
}

function handleError() {
  error.value = true
  loaded.value = true
}

// 🔁 src が変わったら状態をリセット
watch(
  () => props.src,
  () => {
    loaded.value = false
    error.value = false

    // キャッシュ済み画像対策：すでに読み込み済みなら即表示
    if (imgRef.value && imgRef.value.complete) {
      loaded.value = true
    }
  },
  { immediate: true }
)

onMounted(() => {
  // マウント時点で既にキャッシュ済みの場合があるのでケア
  if (imgRef.value && imgRef.value.complete) {
    loaded.value = true
  }
})
</script>

<template>
  <div
    class="async-image-wrapper"
    :class="{ 'async-image-wrapper--rounded': rounded }"
    :style="{ aspectRatio }"
  >
    <!-- 常にDOMにいて、loadedでフェードアウトする -->
    <div 
      class="async-image-skeleton"
      :class="{ 'async-image-skeleton--fadeout': loaded }"
    >
      <div class="async-image-spinner" />
    </div>

    <!-- 正常に読み込めた画像 -->
    <img
      ref="imgRef"
      v-show="!error"
      :src="src"
      :alt="alt"
      class="async-image"
      :class="{ 'async-image--loaded': loaded }"
      loading="lazy"
      @load="handleLoad"
      @error="handleError"
    />

    <!-- 読み込み失敗時のプレースホルダー -->
    <div v-if="error" class="async-image-fallback">
      画像なし
    </div>
  </div>
</template>

<style scoped>
.async-image-wrapper {
  position: relative;
  width: 100%;
  overflow: hidden;
  background: #f5f5f5;
  display: block;
}

.async-image-wrapper--rounded {
  border-radius: 0.75rem;
}

.async-image-skeleton {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 1;
  transition: opacity 0.3s ease-out;
}

.async-image-skeleton--fadeout {
  opacity: 0;
}

/* シンプルなクルクル */
.async-image-spinner {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top-color: rgba(0, 0, 0, 0.4);
  animation: async-image-spin 0.8s linear infinite;
}

@keyframes async-image-spin {
  to {
    transform: rotate(360deg);
  }
}

.async-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  opacity: 0;
  transition: opacity 0.4s ease-out;
}

.async-image--loaded {
  opacity: 1;
}

.async-image-fallback {
  position: absolute;
  inset: 0;
  font-size: 0.75rem;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
