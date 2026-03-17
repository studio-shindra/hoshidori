<script setup>
import { IconTheater } from '@tabler/icons-vue'
import PosterImage from '@/components/PosterImage.vue'

defineProps({
  posterUrl: { type: String, default: null },
  workTitle: { type: String, default: '' },
  workSlug: { type: String, default: null },
  theaterName: { type: String, default: '' },
  watchedOn: { type: String, default: '' },
})
</script>

<template>
  <div class="card-md position-relative">
    <PosterImage :src="posterUrl" :alt="workTitle" :work-slug="workSlug" />
    <div class="ab-bottom dark-gradient text-white">
      <div v-if="theaterName" class="d-flex align-items-center gap-1 small fw-bold">
        <IconTheater size="16" /> {{ theaterName }}
      </div>
      <div class="small fw-bold text-truncate">{{ workTitle }}</div>
      <div v-if="watchedOn" class="text-white-50" style="font-size: 0.65rem">{{ watchedOn }}</div>
    </div>
  </div>
</template>
