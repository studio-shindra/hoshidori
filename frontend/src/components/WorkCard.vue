<script setup>
import { RouterLink } from 'vue-router'
import { IconCalendarEvent, IconMapPin, IconStarFilled } from '@tabler/icons-vue'

defineProps({
  workTitle: { type: String, default: '' },
  workSlug: { type: String, default: null },
  theaterName: { type: String, default: '' },
  watchedOn: { type: String, default: '' },
})
</script>

<template>
  <component
    :is="workSlug ? RouterLink : 'div'"
    :to="workSlug ? `/works/${workSlug}` : undefined"
    class="work-record text-decoration-none text-white"
  >
    <IconStarFilled :size="16" class="work-star" />
    <div class="small fw-bold text-truncate">{{ workTitle }}</div>
    <div v-if="theaterName" class="tiny text-secondary text-truncate mt-2"><IconMapPin :size="11" />{{ theaterName }}</div>
    <div v-if="watchedOn" class="tiny text-secondary text-truncate mt-1"><IconCalendarEvent :size="11" />{{ watchedOn }}</div>
  </component>
</template>

<style scoped>
.work-record { position: relative; display: block; min-height: 118px; padding: 42px 14px 14px; overflow: hidden; border: 1px solid rgba(255,255,255,.1); border-radius: 12px; background: radial-gradient(circle at 80% 10%, rgba(244,63,94,.18), transparent 35%), #18181b; }
.work-record:hover { color: #fff; border-color: rgba(255,255,255,.22); }
.work-star { position: absolute; top: 14px; left: 14px; color: #f43f5e; filter: drop-shadow(0 0 8px rgba(244,63,94,.65)); }
.work-record .tiny { display: flex; align-items: center; gap: 4px; }
</style>
