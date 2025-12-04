<script setup>
import { IconTheater, IconMasksTheater, IconSitemap, IconBrandX, IconBrandInstagram, IconBrandTiktok, IconWorldWww } from '@tabler/icons-vue'

const props = defineProps({
  work: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <div class="body mt-2">
    <div class="title fs-4 fw-bold mb-1">{{ work?.title }}</div>
    <div class="text text-muted">
      <div class="wrap">
        <div class="meta">
          <IconTheater />
          <small class="ms-1">
            <router-link 
              :to="`/works?q=${encodeURIComponent(work?.main_theater?.name)}`" 
              class="text-decoration-none text-muted"
            >
              {{ work?.main_theater?.name }}
            </router-link>
          </small>
        </div>
        <div v-if="work?.troupe" class="team my-2">
          <IconSitemap />
          <small class="ms-1">
            <a 
              v-if="work?.troupe?.official_site"
              :href="work.troupe.official_site" 
              target="_blank" 
              rel="noopener noreferrer"
              class="text-decoration-none text-muted"
            >
              {{ work.troupe.name || work.troupe }}
            </a>
            <router-link 
              v-else
              :to="`/works?q=${encodeURIComponent(work?.troupe?.name || work?.troupe)}`" 
              class="text-decoration-none text-muted"
            >
              {{ work.troupe.name || work.troupe }}
            </router-link>
          </small>
        </div>
        <div v-if="work?.actors && work.actors.length > 0" class="actor mt-2">
          <IconMasksTheater />
          <router-link
            v-for="actor in work.actors"
            :key="actor.id || actor"
            :to="`/works?q=${encodeURIComponent(actor.name || actor)}`"
            class="ms-1 text-decoration-none"
          >
            <small class="text-secondary">{{ actor.name || actor }}</small>
          </router-link>
        </div>
        <div v-if="work?.tags && work.tags.length > 0" class="tag mt-2">
          <router-link
            v-for="tag in work.tags" 
            :key="tag"
            :to="`/works?q=${encodeURIComponent(tag)}`"
            class="badge bg-light text-dark me-1 text-decoration-none"
          >
            {{ tag }}
          </router-link>
        </div>

        <!-- 公式サイト・SNS -->
        <div v-if="work?.official_site || work?.official_x || work?.official_instagram || work?.official_tiktok" class="mt-3">
          <div class="social-icons d-flex gap-2">
            <a v-if="work?.official_site" :href="work.official_site" target="_blank" rel="noopener noreferrer" class="text-dark" title="公式サイト">
              <IconWorldWww :size="24" />
            </a>

            <a v-if="work?.official_x" :href="work.official_x" target="_blank" rel="noopener noreferrer" class="text-dark" title="X">
              <IconBrandX :size="24" />
            </a>
            <a v-if="work?.official_instagram" :href="work.official_instagram" target="_blank" rel="noopener noreferrer" class="text-dark" title="Instagram">
              <IconBrandInstagram :size="24" />
            </a>
            <a v-if="work?.official_tiktok" :href="work.official_tiktok" target="_blank" rel="noopener noreferrer" class="text-dark" title="TikTok">
              <IconBrandTiktok :size="24" />
            </a>
          </div>
        </div>

        <div class="border-top d-flex justify-content-around mt-3 pt-3">
          <div class="wrap df-center gap-1 flex-column">
            <h4 class="badge bg-secondary text-light m-0">コメント数</h4>
            <span class="fs-3 fw-bold">{{ work?.comment_count || 0 }}</span>
          </div>
          <div class="wrap df-center gap-1 flex-column">
            <h4 class="badge bg-secondary text-light m-0">レビュー平均</h4>
            <span class="fs-3 fw-bold">{{ work?.avg_rating ? work.avg_rating.toFixed(1) : '-' }}</span>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
