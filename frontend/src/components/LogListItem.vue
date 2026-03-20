<script setup>
import { IconTheater, IconMapPin, IconThumbUp, IconHeartHandshake, IconSparkles } from '@tabler/icons-vue'
import PosterImage from '@/components/PosterImage.vue'
import { ratingLabel, ratingIcon } from '@/lib/rating'
import { cloudinaryUrl, IMG_TINY } from '@/lib/cloudinary'

const icons = { IconThumbUp, IconHeartHandshake, IconSparkles }

defineProps({
  posterUrl: { type: String, default: null },
  workTitle: { type: String, default: '' },
  workSlug: { type: String, default: null },
  watchedOn: { type: String, default: '' },
  watchedTime: { type: String, default: '' },
  theaterName: { type: String, default: '' },
  theaterArea: { type: String, default: '' },
  memo: { type: String, default: '' },
  rating: { type: Number, default: null },
  images: { type: Array, default: () => [] },
  compact: { type: Boolean, default: false },
})
</script>

<template>
  <div class="card bg-dark border-0 p-2 position-relative">
    <div class="df-center gap-2">
      <div class="card-sm">
        <PosterImage :src="posterUrl" :alt="workTitle" :work-slug="workSlug" size="sm" />
      </div>
      <div class="d-flex flex-column gap-1 min-w-0 flex-grow-1">
        <div class="d-flex justify-content-between align-items-start">
          <div class="fw-bold text-truncate">{{ workTitle }}</div>
          <slot name="action" />
        </div>
        <div class="d-flex align-items-center gap-1 flex-wrap">
          <div v-if="theaterName" class="small text-truncate d-flex align-items-center gap-1">
            <IconTheater size="16" /> {{ theaterName }}
          </div>
          <div v-if="theaterArea" class="small text-truncate d-flex align-items-center gap-1">
            <IconMapPin size="16" /> {{ theaterArea }}
          </div>
        </div>
        <div class="d-flex align-items-center gap-2">
          <div class="small d-flex align-items-center gap-1" v-if="watchedOn">{{ watchedOn }}<span v-if="watchedTime"> {{ watchedTime.slice(0, 5) }}</span></div>
          <span v-if="rating" class="log-rating-badge">
            <component :is="icons[ratingIcon(rating)]" :size="14" />
            {{ ratingLabel(rating) }}
          </span>
        </div>
        <div v-if="images && images.length" class="d-flex gap-1 mt-1">
          <img v-for="img in images" :key="img.id" :src="cloudinaryUrl(img.image_url, IMG_TINY)" class="log-img-thumb rounded" loading="lazy" />
        </div>
        <div v-if="memo" class="small log-memo" :class="compact ? 'text-truncate' : ''">{{ memo }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.log-rating-badge {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
}
.log-img-thumb {
  width: 48px;
  height: 48px;
  object-fit: cover;
  flex-shrink: 0;
}
.log-memo {
  max-width: 100%;
}
</style>
