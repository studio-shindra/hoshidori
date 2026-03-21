<script setup>
import { ref, computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { IconMapPin, IconTicket, IconHeart, IconHeartFilled } from '@tabler/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/lib/api'
import { cloudinaryUrl, IMG_CARD } from '@/lib/cloudinary'

const props = defineProps({
  shop: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['want-to-go-changed'])

const auth = useAuthStore()
const router = useRouter()
const optimizedImage = computed(() => cloudinaryUrl(props.shop.image_src, IMG_CARD))
const wantToGo = ref(!!props.shop.is_want_to_go)
const toggling = ref(false)

async function toggleWantToGo(e) {
  e.preventDefault()
  e.stopPropagation()
  if (!auth.isAuthenticated) {
    router.push({ path: '/login', query: { next: '/' } })
    return
  }
  if (toggling.value) return
  toggling.value = true
  try {
    if (wantToGo.value) {
      await api.delete(`/api/shops/${props.shop.slug}/want-to-go/`)
      wantToGo.value = false
    } else {
      await api.post(`/api/shops/${props.shop.slug}/want-to-go/`)
      wantToGo.value = true
    }
    emit('want-to-go-changed', { slug: props.shop.slug, value: wantToGo.value })
  } catch {
    /* empty */
  } finally {
    toggling.value = false
  }
}
</script>

<template>
  <RouterLink
    :to="`/shops/${shop.slug}`"
    class="shop-card text-decoration-none d-block rounded-3 overflow-hidden"
    :class="shop.is_featured ? 'shop-card-featured' : 'bg-dark'"
  >
    <!-- Thumbnail -->
    <div class="shop-thumb position-relative">
      <img v-if="shop.image_src" :src="optimizedImage" :alt="shop.name" class="shop-thumb-img" loading="lazy" />
      <div v-else class="shop-thumb-img" :class="shop.is_featured ? 'shop-thumb-featured' : ''"></div>
      <span v-if="shop.category" class="shop-tag position-absolute bottom-0 start-0 m-2">
        {{ shop.category }}
      </span>
      <span v-if="shop.is_featured" class="badge badge-featured position-absolute top-0 end-0 m-2">
        おすすめ
      </span>
      <!-- ハートボタン -->
      <button
        class="want-to-go-btn position-absolute"
        @click="toggleWantToGo"
      >
        <IconHeartFilled v-if="wantToGo" :size="18" class="text-rose" />
        <IconHeart v-else :size="18" />
      </button>
    </div>

    <!-- Info -->
    <div class="p-3 d-flex flex-column flex-grow-1">
      <div class="fw-bold text-white">{{ shop.name }}</div>
      <div
        v-if="shop.nearest_station || shop.distance_note"
        class="d-flex align-items-center gap-1 small text-white mt-1"
      >
        <IconMapPin :size="11" />
        <span class="tiny">{{ [shop.nearest_station, shop.distance_note].filter(Boolean).join(' · ') }}</span>
      </div>
      <div v-if="shop.coupon_text" class="mt-auto pt-2">
        <span class="coupon-pill">
          <IconTicket :size="11" />{{ shop.coupon_text }}
        </span>
      </div>
    </div>
  </RouterLink>
</template>

<style scoped>
.shop-card {
  display: flex;
  flex-direction: column;
  height: 100%;
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
.want-to-go-btn {
  bottom: 0.4rem;
  right: 0.4rem;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  backdrop-filter: blur(4px);
  transition: transform 0.15s;
  padding: 0;
  z-index: 2;
}
.want-to-go-btn:hover {
  transform: scale(1.1);
}
.text-rose {
  color: #f43f5e;
}
</style>
