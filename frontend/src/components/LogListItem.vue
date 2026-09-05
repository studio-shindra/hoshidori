<script setup>
import { RouterLink } from 'vue-router'
import { IconMapPin, IconSparkles, IconThumbUp, IconHeartHandshake, IconStarFilled } from '@tabler/icons-vue'
import { ratingIcon, ratingLabel } from '@/lib/rating'
import { cloudinaryUrl, IMG_TINY } from '@/lib/cloudinary'

const icons = { IconThumbUp, IconHeartHandshake, IconSparkles, IconStarFilled }

defineProps({
  workTitle: { type: String, default: '' },
  workSlug: { type: String, default: null },
  watchedOn: { type: String, default: '' },
  watchedTime: { type: String, default: '' },
  theaterName: { type: String, default: '' },
  theaterArea: { type: String, default: '' },
  memo: { type: String, default: '' },
  rating: { type: Number, default: null },
  images: { type: Array, default: () => [] },
  afterShopName: { type: String, default: '' },
  compact: { type: Boolean, default: false },
})
</script>

<template>
  <div class="log-row">
    <component :is="workSlug ? RouterLink : 'div'" :to="workSlug ? `/works/${workSlug}` : undefined" class="log-row-main text-decoration-none text-white">
      <div class="log-date">
        <strong>{{ watchedOn ? watchedOn.slice(8, 10) : '--' }}</strong>
        <span>{{ watchedOn ? `${Number(watchedOn.slice(5, 7))}月` : '' }}</span>
      </div>
      <div class="min-w-0 flex-grow-1">
      <div class="d-flex justify-content-between align-items-start gap-2">
        <div class="fw-bold text-truncate">{{ workTitle }}</div>
      </div>
      <div class="d-flex align-items-center gap-2 flex-wrap mt-1">
        <span v-if="watchedTime" class="tiny text-secondary">{{ watchedTime.slice(0, 5) }}</span>
        <span v-if="theaterName" class="tiny text-secondary text-truncate"><IconMapPin :size="11" />{{ theaterName }}<template v-if="theaterArea">・{{ theaterArea }}</template></span>
        <span v-if="rating" class="log-rating"><component :is="icons[ratingIcon(rating)]" :size="12" />{{ ratingLabel(rating) }}</span>
      </div>
      <div v-if="afterShopName" class="after-shop mt-2"><IconSparkles :size="12" />感想戦：{{ afterShopName }}</div>
      <div v-if="images.length" class="d-flex gap-1 mt-2">
        <img v-for="image in images" :key="image.id" :src="cloudinaryUrl(image.image_url, IMG_TINY)" class="log-img-thumb rounded" loading="lazy" />
      </div>
      <div v-if="memo" class="small text-white-50 mt-2" :class="{ 'text-truncate': compact }">{{ memo }}</div>
      </div>
    </component>
    <div v-if="$slots.action" class="log-row-action"><slot name="action" /></div>
  </div>
</template>

<style scoped>
.log-row { position: relative; border: 1px solid rgba(255,255,255,.09); border-radius: 12px; background: #18181b; }
.log-row-main { display: flex; width: 100%; min-width: 0; gap: 12px; padding: 13px 44px 13px 13px; }
.log-row-main > .min-w-0 { min-width: 0; }
.log-row-action { position: absolute; top: 0; right: 0; z-index: 2; padding: 12px; }
.log-row:hover { color: #fff; border-color: rgba(255,255,255,.2); }
.log-date { width: 48px; min-width: 48px; height: 56px; display: flex; flex-direction: column; align-items: center; justify-content: center; border-right: 1px dashed rgba(255,255,255,.18); color: #a1a1aa; font-size: .66rem; }
.log-date strong { color: #fff; font-size: 1.25rem; line-height: 1; }
.log-row .tiny { display: inline-flex; align-items: center; gap: 3px; }
.log-rating { display: inline-flex; align-items: center; gap: 3px; color: #f59e0b; font-size: .68rem; font-weight: 700; }
.after-shop { display: flex; align-items: center; gap: 4px; color: #fda4af; font-size: .72rem; }
.log-img-thumb { width: 42px; height: 42px; object-fit: cover; }
</style>
