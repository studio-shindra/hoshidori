<script setup>
import { IconMasksTheater } from '@tabler/icons-vue'
import UserAvatar from '@/components/UserAvatar.vue'

defineProps({
  src: {
    type: String,
    default: null,
  },
  alt: {
    type: String,
    default: '',
  },
  workSlug: {
    type: String,
    default: null,
  },
  credit: {
    type: String,
    default: null,
  },
  creditAvatar: {
    type: String,
    default: null,
  },
})
</script>

<template>
  <div class="poster-image">
    <component :is="workSlug ? 'router-link' : 'div'" :to="workSlug ? `/works/${workSlug}` : undefined" class="poster-link">
      <img v-if="src" :src="src" :alt="alt" />
      <div v-else class="poster-placeholder">
        <IconMasksTheater :size="24" class="text-secondary" />
        <span class="small text-secondary mt-1">No Image</span>
      </div>
      <span v-if="src && credit" class="poster-credit"><UserAvatar :src="creditAvatar" :name="credit" :size="24" /></span>
    </component>
  </div>
</template>

<style scoped>
.poster-image {
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: 0.5rem;
  overflow: hidden;
  background: #27272a;
  position: relative;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.poster-link {
  display: block;
  width: 100%;
  height: 100%;
  text-decoration: none;
}

.poster-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px dashed #3f3f46;
  border-radius: 0.5rem;
}

.poster-credit {
  position: absolute;
  top: 0.4rem;
  right: 0.4rem;
}
</style>
