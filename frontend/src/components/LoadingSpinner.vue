<script setup>
import { ref, onMounted, watch } from 'vue'
import { gsap } from 'gsap'

const props = defineProps({
  show: {
    type: Boolean,
    default: true
  }
})

const iconRef = ref(null)
const containerRef = ref(null)
const canFadeOut = ref(false)
const isVisible = ref(true) // DOMに表示するかどうか

onMounted(() => {
  if (iconRef.value) {
    // 最初にバウンスして登場
    gsap.from(iconRef.value, {
      duration: 1,
      scale: 0,
      ease: 'elastic.out(1, 0.3)',
      onComplete: () => {
        // バウンス完了
        canFadeOut.value = true
        
        // ロードが既に終わっていたらフェードアウト開始
        if (!props.show && containerRef.value) {
          gsap.to(containerRef.value, {
            duration: 0.5,
            opacity: 0,
            ease: 'power2.out',
            onComplete: () => {
              isVisible.value = false
            }
          })
        }
        
        // バウンス終了後、0.5秒待ってから回転開始
        gsap.to(iconRef.value, {
          duration: 2.5,
          rotation: 360,
          ease: 'power3.out',
          repeat: -1,
          yoyo: false,
          delay: 0.5,
        })
      }
    })
  }
})

// showがfalseになったらフェードアウト（バウンス完了後のみ）
watch(() => props.show, (newValue) => {
  if (!newValue && containerRef.value && canFadeOut.value) {
    gsap.to(containerRef.value, {
      duration: 0.5,
      opacity: 0,
      ease: 'power2.out',
      onComplete: () => {
        isVisible.value = false
      }
    })
  }
})
</script>

<template>
  <div v-if="isVisible" ref="containerRef" class="loading-spinner">
    <div class="spinner-container">
      <img
        ref="iconRef"
        src="/icon.svg"
        alt="Loading..."
        class="spinner-icon"
      />
    </div>
  </div>
</template>

<style scoped>
.loading-spinner {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(255, 255, 255, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  opacity: 1;
}

.spinner-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner-icon {
  width: 80px;
  height: 80px;
}
</style>
