<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { IconExternalLink, IconMapPin, IconSparkles, IconHeart, IconHeartFilled } from '@tabler/icons-vue'
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
const isGooglePlace = computed(() => props.shop.source === 'google_places')
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

function openManualShop() {
  if (!isGooglePlace.value) router.push(`/shops/${props.shop.slug}`)
}
</script>

<template>
  <component
    :is="isGooglePlace ? 'a' : 'div'"
    :href="isGooglePlace ? shop.google_map_url : undefined"
    :target="isGooglePlace ? '_blank' : undefined"
    :rel="isGooglePlace ? 'noopener noreferrer' : undefined"
    :role="isGooglePlace ? undefined : 'link'"
    :tabindex="isGooglePlace ? undefined : 0"
    class="shop-card text-decoration-none d-block rounded-3 overflow-hidden"
    :class="{
      'shop-card-sponsored': shop.listing_tier === 'sponsored',
      'shop-card-recognized': shop.listing_tier === 'recognized',
      'shop-card-listed': shop.listing_tier === 'listed',
      'shop-card-google': isGooglePlace,
      'shop-card-text-only': !isGooglePlace && !shop.image_src,
    }"
    @click="openManualShop"
    @keydown.enter="openManualShop"
  >
    <template v-if="isGooglePlace">
      <div class="google-place-row">
        <div class="d-flex align-items-center justify-content-between gap-3">
          <div class="google-place-name">{{ shop.name }}</div>
          <IconExternalLink :size="15" class="google-external-icon" />
        </div>
        <div class="google-place-meta">
          <span v-if="shop.category" class="google-category">{{ shop.category }}</span>
          <span v-if="shop.distance_note || shop.address" class="google-distance">
            <IconMapPin :size="12" />{{ shop.distance_note || shop.address }}
          </span>
        </div>
      </div>
    </template>

    <template v-else>
      <!-- Thumbnail -->
      <div v-if="shop.image_src" class="shop-thumb position-relative">
        <img :src="optimizedImage" :alt="shop.name" class="shop-thumb-img" loading="lazy" />
        <div v-if="shop.category || ['sponsored', 'recognized', 'listed'].includes(shop.listing_tier)" class="shop-labels position-absolute bottom-0 start-0 m-2">
          <span v-if="shop.category" class="shop-tag">{{ shop.category }}</span>
          <span v-if="shop.listing_tier === 'sponsored'" class="shop-recommend-tag">ホシドリおすすめ店</span>
          <span v-else-if="shop.listing_tier === 'recognized'" class="shop-recognized-tag">ホシドリ認定店</span>
          <span v-else-if="shop.listing_tier === 'listed'" class="shop-listed-tag">掲載店</span>
        </div>
        <div v-if="shop.image_source === 'google_places'" class="google-photo-credit" @click.stop>
          <a
            :href="shop.google_photo_maps_uri || shop.google_map_url"
            target="_blank"
            rel="noopener noreferrer"
            @click.stop
          >Google Maps</a>
          <template v-for="author in shop.google_photo_attributions" :key="author.display_name">
            <span> · </span>
            <a
              :href="author.uri || shop.google_photo_maps_uri || shop.google_map_url"
              target="_blank"
              rel="noopener noreferrer"
              @click.stop
            >{{ author.display_name }}</a>
          </template>
        </div>
        <!-- ハートボタン -->
        <button class="want-to-go-btn position-absolute" :aria-label="wantToGo ? `${shop.name}の行きたいを取り消す` : `${shop.name}を行きたいに追加`" @click="toggleWantToGo">
          <IconHeartFilled v-if="wantToGo" :size="18" class="text-rose" />
          <IconHeart v-else :size="18" />
        </button>
      </div>

      <button v-else class="want-to-go-btn want-to-go-text position-absolute" :aria-label="wantToGo ? `${shop.name}の行きたいを取り消す` : `${shop.name}を行きたいに追加`" @click="toggleWantToGo">
        <IconHeartFilled v-if="wantToGo" :size="18" class="text-rose" />
        <IconHeart v-else :size="18" />
      </button>

      <!-- Info -->
      <div class="p-3 d-flex flex-column flex-grow-1">
        <div v-if="!shop.image_src && (shop.category || ['sponsored', 'recognized', 'listed'].includes(shop.listing_tier))" class="shop-labels mb-2">
          <span v-if="shop.category" class="shop-tag shop-tag-static">{{ shop.category }}</span>
          <span v-if="shop.listing_tier === 'sponsored'" class="shop-recommend-tag shop-tag-static">ホシドリおすすめ店</span>
          <span v-else-if="shop.listing_tier === 'recognized'" class="shop-recognized-tag shop-tag-static">ホシドリ認定店</span>
          <span v-else-if="shop.listing_tier === 'listed'" class="shop-listed-tag shop-tag-static">掲載店</span>
        </div>
        <div class="shop-name-row">
          <span v-if="shop.listing_tier === 'sponsored'" class="listing-mark" aria-hidden="true"></span>
          <div class="fw-bold text-white">{{ shop.name }}</div>
        </div>
        <div
          v-if="shop.nearest_station || shop.distance_note"
          class="d-flex align-items-center gap-1 small text-white mt-1"
        >
          <IconMapPin :size="11" />
          <span class="tiny text-truncate">{{ [shop.nearest_station, shop.distance_note].filter(Boolean).join(' · ') }}</span>
        </div>
        <div v-if="shop.benefit_text || shop.after_viewing_count || shop.listing_tier === 'sponsored'" class="shop-info-footer mt-auto pt-2">
          <span v-if="shop.benefit_text" class="benefit-pill">
            <IconSparkles :size="11" />{{ shop.benefit_text }}
          </span>
          <span v-else-if="shop.after_viewing_count" class="tiny color-rose">
            感想戦に選ばれた {{ shop.after_viewing_count }}回
          </span>
          <span v-else></span>
          <span v-if="shop.listing_tier === 'sponsored'" class="listing-pr">PR</span>
        </div>
      </div>
    </template>
  </component>
</template>

<style scoped>
.shop-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  transition: opacity 0.15s;
  cursor: pointer;
  &:hover { opacity: 0.85; }
}
.google-photo-credit {
  position: absolute;
  right: 7px;
  bottom: 7px;
  z-index: 2;
  max-width: calc(100% - 14px);
  padding: 3px 6px;
  overflow: hidden;
  border-radius: 5px;
  color: #d4d4d8;
  background: rgba(0,0,0,.66);
  font: 500 .52rem/1.3 Roboto, sans-serif;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.google-photo-credit a { color: #fff; text-decoration: none; }
.shop-card-sponsored {
  background: #1c1917;
  border: 0;
}
.shop-card-recognized { background: #18181b; border: 0; }
.shop-card-listed { background: #18181b; border: 0; }
.shop-card-text-only {
  position: relative;
  width: 100%;
  height: auto;
  min-height: 126px;
  align-self: flex-start;
  background: #18181b;
  border: 1px solid rgba(255,255,255,.08);
}
.shop-card-text-only > .p-3 { padding-right: 3rem !important; }
.shop-card-text-only.shop-card-sponsored { background: #1c1917; border-color: rgba(251,191,36,.12); }
.shop-card-google { background: transparent; border: 0; border-bottom: 1px solid rgba(255,255,255,.08); border-radius: 0 !important; }
.shop-card-google:hover { opacity: 1; background: rgba(255,255,255,.025); }
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
.shop-tag {
  background: rgba(0, 0, 0, 0.6);
  color: #e4e4e7;
  font-size: 0.65rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  backdrop-filter: blur(4px);
}
.shop-labels { display: flex; align-items: center; gap: .35rem; }
.shop-tag-static { background: rgba(255,255,255,.06); backdrop-filter: none; }
.shop-recommend-tag { padding: .2rem .5rem; border-radius: 4px; background: rgba(10,10,11,.68); color: #fde68a; font-size: .62rem; font-weight: 700; backdrop-filter: blur(4px); }
.shop-recognized-tag { padding: .2rem .5rem; border-radius: 4px; background: rgba(244,63,94,.14); color: #fecdd3; font-size: .62rem; font-weight: 700; backdrop-filter: blur(4px); }
.shop-listed-tag { padding: .2rem .5rem; border-radius: 4px; background: rgba(255,255,255,.08); color: #d4d4d8; font-size: .62rem; font-weight: 650; backdrop-filter: blur(4px); }
.shop-name-row { display: flex; align-items: center; gap: .4rem; }
.listing-mark { width: 19px; height: 19px; flex: 0 0 auto; background: #fff; filter: drop-shadow(0 0 4px rgba(251,191,36,.9)) drop-shadow(0 0 9px rgba(245,158,11,.5)); -webkit-mask: url('/icon.svg') center / contain no-repeat; mask: url('/icon.svg') center / contain no-repeat; }
.shop-info-footer { display: flex; align-items: flex-end; justify-content: space-between; gap: .5rem; }
.listing-pr { flex: 0 0 auto; padding-bottom: .08rem; color: rgba(255,255,255,.28); font-size: .5rem; font-weight: 700; letter-spacing: .08em; }
.google-place-row { padding: .85rem .15rem .9rem; }
.google-place-name { color: #f4f4f5; font-size: .9rem; font-weight: 700; }
.google-external-icon { flex: 0 0 auto; color: #71717a; }
.google-place-meta { display: flex; align-items: center; flex-wrap: wrap; gap: .45rem .6rem; margin-top: .45rem; }
.google-category { padding: .15rem .45rem; border: 1px solid rgba(255,255,255,.1); border-radius: 99px; color: #a1a1aa; font-size: .64rem; }
.google-distance { display: inline-flex; align-items: center; gap: 3px; color: #a1a1aa; font-size: .68rem; }
.benefit-pill {
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
  top: 0.4rem;
  bottom: auto;
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
.want-to-go-text { top: .65rem; right: .65rem; background: rgba(255,255,255,.05); }
.text-rose {
  color: #f43f5e;
}
</style>
