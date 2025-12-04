<script setup>
import { ref } from 'vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const showSpinner = ref(true)
</script>

<template>
  <div class="test-page">
    <LoadingSpinner v-if="showSpinner" />
    
    <div v-else class="container py-4">
      <h1>ローディングテスト</h1>
      <p>スピナーが非表示になりました</p>
    </div>

    <div class="controls">
      <button 
        @click="showSpinner = !showSpinner"
        class="btn btn-primary"
      >
        {{ showSpinner ? 'スピナーを隠す' : 'スピナーを表示' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.test-page {
  min-height: 100vh;
  position: relative;
}

.controls {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10000;
}
</style>
