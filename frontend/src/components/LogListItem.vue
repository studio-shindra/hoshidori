<script setup>
import { IconTheater, IconMapPin, IconThumbUp, IconHeartHandshake, IconSparkles } from '@tabler/icons-vue'
import PosterImage from '@/components/PosterImage.vue'
import { ratingLabel, ratingIcon } from '@/lib/rating'

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
})
</script>

<template>
  <div class="card bg-dark border-0 p-2 position-relative">
    <div class="df-center gap-2">
      <div class="card-sm">
        <PosterImage :src="posterUrl" :alt="workTitle" :work-slug="workSlug" />
      </div>
      <div class="d-flex flex-column gap-1 min-w-0 flex-grow-1">
        <div class="d-flex justify-content-between align-items-start">
          <div class="fw-bold text-truncate">{{ workTitle }}</div>
          <slot name="action" />
        </div>
        <div class="d-flex align-items-center gap-1">
          <div v-if="theaterName" class="small text-truncate d-flex align-items-center gap-1">
            <IconTheater size="16" /> {{ theaterName }}
          </div>
          <div v-if="theaterArea" class="small text-truncate d-flex align-items-center gap-1">
            <IconMapPin size="16" /> {{ theaterArea }}
          </div>
        </div>
        <div class="d-flex justify-content-start flex-column">
          <div class="small d-flex align-items-center gap-1" v-if="watchedOn">{{ watchedOn }}<span v-if="watchedTime"> {{ watchedTime.slice(0, 5) }}</span></div>
          <span v-if="rating" class="df-center gap-1 bg-amber text-white fw-bold p-1 rounded mt-3">
            <component :is="icons[ratingIcon(rating)]" :size="20" />
            {{ ratingLabel(rating) }}
          </span>
        </div>
      </div>
    </div>
    <div v-if="memo" class="small text-truncate p-2 border-top border-secondary mt-3">{{ memo }}</div>
  </div>
</template>
