<script setup>
import { IconHeartHandshake, IconThumbUp, IconSparkles } from '@tabler/icons-vue'
import { RATING_OPTIONS } from '@/lib/rating'

const icons = { IconHeartHandshake, IconThumbUp, IconSparkles }

const model = defineModel({ default: '' })
</script>

<template>
  <div class="d-flex gap-2">
    <button
      v-for="opt in RATING_OPTIONS"
      :key="opt.value"
      type="button"
      class="rating-btn flex-fill small d-flex align-items-center justify-content-center gap-1 flex-column"
      :class="{ 'is-active': model === opt.value }"
      @click="model = model === opt.value ? '' : opt.value"
    >
      <component :is="icons[opt.icon]" :size="30" />
      {{ opt.label }}
    </button>
  </div>
</template>

<style scoped>
.rating-btn {
  background: #333;
  color: white;
  border: none;
  padding: 0.4rem 0.75rem;
  border-radius: 0.375rem;
  cursor: pointer;

  &.is-active {
    background: #f59e0b;
    color: #fff;
  }
}
</style>
