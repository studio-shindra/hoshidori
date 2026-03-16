<script setup>
import { RouterLink } from 'vue-router'
import { IconMapPin, IconTicket } from '@tabler/icons-vue'

defineProps({
  shop: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <RouterLink
    :to="`/shops/${shop.slug}`"
    class="shop-card text-decoration-none d-block rounded-3 overflow-hidden"
    :class="shop.is_featured ? 'shop-card-featured' : 'bg-dark'"
  >
    <!-- Thumbnail -->
    <div class="shop-thumb position-relative">
      <img v-if="shop.image_src" :src="shop.image_src" :alt="shop.name" class="shop-thumb-img" />
      <div v-else class="shop-thumb-img" :class="shop.is_featured ? 'shop-thumb-featured' : ''"></div>
      <span v-if="shop.category" class="shop-tag position-absolute bottom-0 start-0 m-2">
        {{ shop.category }}
      </span>
      <span v-if="shop.is_featured" class="badge badge-featured position-absolute top-0 end-0 m-2">
        おすすめ
      </span>
    </div>

    <!-- Info -->
    <div class="p-3">
      <div class="fw-bold text-white">{{ shop.name }}</div>
      <div
        v-if="shop.nearest_station || shop.distance_note"
        class="d-flex align-items-center gap-1 small text-white mt-1"
      >
        <IconMapPin :size="11" />
        <span>{{ [shop.nearest_station, shop.distance_note].filter(Boolean).join(' · ') }}</span>
      </div>
      <div v-if="shop.coupon_text" class="mt-2">
        <span class="coupon-pill">
          <IconTicket :size="11" />{{ shop.coupon_text }}
        </span>
      </div>
    </div>
  </RouterLink>
</template>

<style scoped>
.shop-card {
  transition: opacity 0.15s;
  &:hover { opacity: 0.85; }
}
.shop-card-featured {
  background: #1c1917;
  border: 1px solid rgba(245, 158, 11, 0.3);
}
.shop-thumb {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}
.shop-thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: linear-gradient(135deg, #27272a 0%, #3f3f46 100%);
}
.shop-thumb-featured {
  background: linear-gradient(135deg, #44403c 0%, #57534e 50%, #44403c 100%);
}
.shop-tag {
  background: rgba(0, 0, 0, 0.6);
  color: #e4e4e7;
  font-size: 0.65rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  backdrop-filter: blur(4px);
}
.coupon-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: rgba(244, 63, 94, 0.12);
  color: #f43f5e;
  border: 1px solid rgba(244, 63, 94, 0.25);
  font-size: 0.7rem;
  padding: 0.2rem 0.6rem;
  border-radius: 99px;
}
</style>
