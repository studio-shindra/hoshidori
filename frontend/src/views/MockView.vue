<script setup>
import 'bootstrap/dist/css/bootstrap.min.css'
import { ref, computed } from 'vue'

const page = ref('top')
const selectedWork = ref(null)

// ダミーデータ
const works = [
  {
    id: 1,
    title: 'ハムレット',
    company: '劇団四季',
    theater: '本多劇場',
    date: '2026.03.15 – 04.10',
    hasImage: true,
    imageBy: '@sakura_stage',
    status: 'planned',
    reviewCount: 3,
  },
  {
    id: 2,
    title: '銀河鉄道の夜',
    company: 'カンパニーデラシネラ',
    theater: 'シアタートラム',
    date: '2026.04.01 – 04.20',
    hasImage: false,
    imageBy: null,
    status: 'watched',
    reviewCount: 5,
  },
  {
    id: 3,
    title: 'マクベス',
    company: 'NODA・MAP',
    theater: '東京芸術劇場',
    date: '2026.05.01 – 05.30',
    hasImage: true,
    imageBy: '@theater_fan99',
    status: null,
    reviewCount: 0,
  },
]

const reviews = [
  {
    id: 1,
    user: 'miki_theater',
    body: '圧倒的な演技力。3幕の独白シーンで涙が止まらなかった。もう一度観に行きたい。',
    tags: ['感動', '演技が最高'],
    likes: 24,
    liked: false,
  },
  {
    id: 2,
    user: 'stage_lover_22',
    body: '演出が斬新で飽きさせない構成。照明の使い方がとても印象的だった。',
    tags: ['演出'],
    likes: 12,
    liked: true,
  },
  {
    id: 3,
    user: 'gekidan_watcher',
    body: '友人に勧められて初めて観劇。想像以上に引き込まれた。',
    tags: ['初観劇'],
    likes: 8,
    liked: false,
  },
]

const shops = [
  {
    id: 1,
    name: 'Cafe Shimokita',
    genre: 'カフェ・軽食',
    description: '観劇前後にぴったりの落ち着いた空間',
    distance: '徒歩3分',
    coupon: 'ドリンク10%OFF',
    featured: true,
  },
  {
    id: 2,
    name: '居酒屋 幕間',
    genre: '居酒屋・和食',
    description: '観劇帰りの一杯に最適',
    distance: '徒歩5分',
    coupon: 'お通し無料',
    featured: false,
  },
  {
    id: 3,
    name: 'ビストロ カーテンコール',
    genre: 'フレンチビストロ',
    description: '記念日ディナーにもおすすめ',
    distance: '徒歩7分',
    coupon: null,
    featured: false,
  },
]

const sortedShops = computed(() => [...shops].sort((a, b) => (b.featured ? 1 : 0) - (a.featured ? 1 : 0)))
const plannedWorks = computed(() => works.filter((w) => w.status === 'planned'))
const watchedWorks = computed(() => works.filter((w) => w.status === 'watched'))
const plannedCount = computed(() => plannedWorks.value.length)
const watchedCount = computed(() => watchedWorks.value.length)
const reviewCount = computed(() => works.reduce((s, w) => s + w.reviewCount, 0))

function openWork(w) {
  selectedWork.value = w
  page.value = 'work'
}

function toggleLike(r) {
  r.liked = !r.liked
  r.likes += r.liked ? 1 : -1
}

// 記録投稿 state
const postWork = ref('')
const postStatus = ref('watched')
const postMemo = ref('')

// ポスター投稿 state
const posterWork = ref(null)
</script>

<template>
  <div class="mock-shell" data-bs-theme="dark">
    <!-- ========== TOP ========== -->
    <template v-if="page === 'top'">
      <header class="d-flex align-items-center justify-content-between px-3 pt-4 pb-2">
        <h1 class="fs-4 fw-bold mb-0 mock-brand">HOSHIDORI</h1>
        <button class="btn btn-link text-secondary p-0 fs-5">🔍</button>
      </header>

      <!-- Stats -->
      <div class="row g-2 px-3 mb-4">
        <div class="col-4">
          <div class="card bg-dark border-0 text-center py-3">
            <div class="fs-3 fw-bold mock-color-amber">{{ plannedCount }}</div>
            <div class="small text-secondary">これから観る</div>
          </div>
        </div>
        <div class="col-4">
          <div class="card bg-dark border-0 text-center py-3">
            <div class="fs-3 fw-bold mock-color-green">{{ watchedCount }}</div>
            <div class="small text-secondary">観た</div>
          </div>
        </div>
        <div class="col-4">
          <div class="card bg-dark border-0 text-center py-3">
            <div class="fs-3 fw-bold text-light">{{ reviewCount }}</div>
            <div class="small text-secondary">感想</div>
          </div>
        </div>
      </div>

      <!-- これから観る -->
      <section v-if="plannedWorks.length" class="mb-4">
        <h2 class="small fw-semibold text-secondary px-3 mb-3">これから観る</h2>
        <div class="d-flex gap-3 px-3 overflow-auto mock-scroll-hide">
          <div
            v-for="w in plannedWorks"
            :key="w.id"
            class="mock-card-sm"
            role="button"
            @click="openWork(w)"
          >
            <div v-if="w.hasImage" class="mock-poster-sm mock-poster-gradient">
              <span class="mock-credit">📷 {{ w.imageBy }}</span>
            </div>
            <div v-else class="mock-poster-sm mock-poster-empty">
              <span class="fs-4">🎭</span>
              <span class="mock-tiny text-secondary">ポスター画像募集中</span>
            </div>
            <div class="mt-2">
              <div class="small fw-medium text-truncate">{{ w.title }}</div>
              <div class="mock-tiny text-secondary text-truncate">{{ w.company }}</div>
              <span class="badge mock-badge-amber mt-1">これから観る</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 最近観た -->
      <section v-if="watchedWorks.length" class="mb-4">
        <h2 class="small fw-semibold text-secondary px-3 mb-3">最近観た作品</h2>
        <div class="d-flex flex-column gap-3 px-3">
          <div
            v-for="w in watchedWorks"
            :key="w.id"
            class="card bg-dark border-0 p-3"
            role="button"
            @click="openWork(w)"
          >
            <div class="d-flex gap-3">
              <div v-if="w.hasImage" class="mock-thumb mock-poster-gradient"></div>
              <div v-else class="mock-thumb mock-poster-empty-sm">🎭</div>
              <div class="flex-grow-1 min-w-0">
                <div class="fw-medium small text-truncate">{{ w.title }}</div>
                <div class="mock-tiny text-secondary">{{ w.company }} / {{ w.theater }}</div>
                <div class="mock-tiny text-secondary mt-1">{{ w.date }}</div>
                <div class="d-flex align-items-center gap-2 mt-1">
                  <span class="badge mock-badge-green">観た</span>
                  <span v-if="w.reviewCount" class="mock-tiny text-secondary">📝 {{ w.reviewCount }}件</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- すべての作品 -->
      <section class="mb-5">
        <h2 class="small fw-semibold text-secondary px-3 mb-3">すべての作品</h2>
        <div class="d-flex flex-column gap-3 px-3">
          <div
            v-for="w in works"
            :key="w.id"
            class="card bg-dark border-0 p-3"
            role="button"
            @click="openWork(w)"
          >
            <div class="d-flex gap-3">
              <div v-if="w.hasImage" class="mock-thumb mock-poster-gradient"></div>
              <div v-else class="mock-thumb mock-poster-empty-sm">🎭</div>
              <div class="flex-grow-1 min-w-0">
                <div class="fw-medium small text-truncate">{{ w.title }}</div>
                <div class="mock-tiny text-secondary">{{ w.company }} / {{ w.theater }}</div>
                <div class="mock-tiny text-secondary mt-1">{{ w.date }}</div>
                <div class="d-flex align-items-center gap-2 mt-1">
                  <span v-if="w.status === 'planned'" class="badge mock-badge-amber">これから観る</span>
                  <span v-else-if="w.status === 'watched'" class="badge mock-badge-green">観た</span>
                  <span v-if="w.reviewCount" class="mock-tiny text-secondary">📝 {{ w.reviewCount }}件</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </template>

    <!-- ========== WORK DETAIL ========== -->
    <template v-if="page === 'work' && selectedWork">
      <!-- Hero -->
      <div class="position-relative">
        <div v-if="selectedWork.hasImage" class="mock-hero mock-poster-gradient"></div>
        <div v-else class="mock-hero mock-poster-empty-hero">
          <span class="fs-1">🎭</span>
          <span class="text-secondary small">ポスター画像募集中</span>
          <button class="btn btn-sm btn-outline-secondary mt-2" @click="posterWork = selectedWork; page = 'poster'">
            最初の1枚を投稿
          </button>
        </div>
        <button class="btn btn-dark btn-sm position-absolute top-0 start-0 m-3 rounded-circle mock-back" @click="page = 'top'">
          ←
        </button>
        <div class="mock-hero-fade"></div>
      </div>

      <!-- Info -->
      <div class="px-3 position-relative" style="margin-top: -2.5rem; z-index: 2">
        <h2 class="fs-5 fw-bold mb-1">{{ selectedWork.title }}</h2>
        <div class="small text-secondary">{{ selectedWork.company }}</div>
        <div class="small text-secondary">{{ selectedWork.theater }} · {{ selectedWork.date }}</div>

        <div class="mock-tiny text-secondary mt-2">
          <template v-if="selectedWork.hasImage">
            Top image by <span class="text-light">{{ selectedWork.imageBy }}</span>
            · <button class="btn btn-link btn-sm p-0 mock-tiny text-secondary" @click="posterWork = selectedWork; page = 'poster'">写真を投稿</button>
          </template>
          <template v-else>
            ポスター画像募集中
          </template>
        </div>

        <div v-if="selectedWork.status" class="mt-2">
          <span v-if="selectedWork.status === 'planned'" class="badge mock-badge-amber">これから観る</span>
          <span v-else-if="selectedWork.status === 'watched'" class="badge mock-badge-green">観た</span>
        </div>

        <!-- Action buttons -->
        <div class="d-flex gap-2 mt-3">
          <button class="btn btn-dark flex-fill mock-color-amber fw-medium">これから観る</button>
          <button class="btn btn-dark flex-fill mock-color-green fw-medium">観た</button>
          <button class="btn mock-btn-primary flex-fill fw-medium" @click="page = 'record'">感想を書く</button>
        </div>
      </div>

      <!-- Reviews -->
      <section class="mt-4 px-3">
        <h3 class="small fw-semibold text-secondary mb-3">みんなの感想</h3>
        <div class="d-flex flex-column gap-3">
          <div v-for="r in reviews" :key="r.id" class="card bg-dark border-0 p-3">
            <div class="d-flex align-items-center gap-2 mb-2">
              <div class="mock-avatar">{{ r.user[0].toUpperCase() }}</div>
              <span class="small fw-medium">{{ r.user }}</span>
            </div>
            <div v-if="r.tags.length" class="d-flex gap-1 flex-wrap mb-2">
              <span v-for="tag in r.tags" :key="tag" class="badge bg-secondary bg-opacity-25 text-secondary fw-normal">
                #{{ tag }}
              </span>
            </div>
            <p class="small text-light mb-2 lh-base">{{ r.body }}</p>
            <button
              class="btn btn-link btn-sm p-0 text-decoration-none small"
              :class="r.liked ? 'mock-color-rose' : 'text-secondary'"
              @click="toggleLike(r)"
            >
              ♥ {{ r.likes }}
            </button>
          </div>
        </div>
      </section>

      <!-- Nearby shops -->
      <section class="mt-4 px-3 mb-5">
        <h3 class="small fw-semibold text-secondary mb-3">
          {{ selectedWork.theater }} の近くの店
        </h3>
        <div class="d-flex flex-column gap-3">
          <div
            v-for="s in sortedShops"
            :key="s.id"
            class="card border-0 p-0 overflow-hidden"
            :class="s.featured ? 'mock-shop-featured' : 'bg-dark'"
          >
            <div class="position-relative">
              <!-- shop image -->
              <div class="mock-shop-img" :class="s.featured ? 'mock-shop-img-featured' : ''"></div>
              <span v-if="s.featured" class="badge mock-badge-featured position-absolute top-0 start-0 m-2">
                おすすめ
              </span>
            </div>
            <div class="p-3">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <div class="fw-medium small">{{ s.name }}</div>
                  <div class="mock-tiny text-secondary">{{ s.genre }} · {{ s.distance }}</div>
                  <div class="mock-tiny text-secondary mt-1">{{ s.description }}</div>
                </div>
                <button v-if="s.coupon" class="btn btn-sm mock-btn-coupon flex-shrink-0 ms-2">
                  {{ s.coupon }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </template>

    <!-- ========== RECORD POST ========== -->
    <template v-if="page === 'record'">
      <header class="d-flex align-items-center justify-content-between px-3 pt-4 pb-3">
        <button class="btn btn-link text-secondary p-0 small text-decoration-none" @click="page = selectedWork ? 'work' : 'top'">
          ← 戻る
        </button>
        <h1 class="fs-6 fw-bold mb-0">記録する</h1>
        <div style="width: 48px"></div>
      </header>

      <div class="px-3 d-flex flex-column gap-4">
        <!-- 作品選択 -->
        <div>
          <label class="form-label mock-tiny text-secondary">作品</label>
          <select v-model="postWork" class="form-select bg-dark border-secondary text-light">
            <option value="" disabled>作品を選択</option>
            <option v-for="w in works" :key="w.id" :value="w.id">
              {{ w.title }} / {{ w.company }}
            </option>
          </select>
        </div>

        <!-- ステータス切替 -->
        <div>
          <label class="form-label mock-tiny text-secondary">ステータス</label>
          <div class="d-flex gap-2">
            <button
              class="btn flex-fill fw-medium"
              :class="postStatus === 'planned' ? 'mock-btn-status-amber' : 'btn-dark text-secondary'"
              @click="postStatus = 'planned'"
            >
              これから観る
            </button>
            <button
              class="btn flex-fill fw-medium"
              :class="postStatus === 'watched' ? 'mock-btn-status-green' : 'btn-dark text-secondary'"
              @click="postStatus = 'watched'"
            >
              観た
            </button>
          </div>
        </div>

        <!-- メモ / 感想 -->
        <div>
          <label class="form-label mock-tiny text-secondary">メモ / 感想</label>
          <textarea
            v-model="postMemo"
            rows="6"
            placeholder="観劇の感想やメモを書く..."
            class="form-control bg-dark border-secondary text-light"
          ></textarea>
        </div>

        <!-- Buttons -->
        <div class="d-flex gap-2 mt-2 mb-5">
          <button class="btn btn-dark flex-fill fw-medium text-secondary">下書き保存</button>
          <button class="btn mock-btn-primary flex-fill fw-medium">投稿する</button>
        </div>
      </div>
    </template>

    <!-- ========== POSTER UPLOAD ========== -->
    <template v-if="page === 'poster'">
      <header class="d-flex align-items-center justify-content-between px-3 pt-4 pb-3">
        <button class="btn btn-link text-secondary p-0 small text-decoration-none" @click="page = selectedWork ? 'work' : 'top'">
          ← 戻る
        </button>
        <h1 class="fs-6 fw-bold mb-0">ポスター写真を投稿</h1>
        <div style="width: 48px"></div>
      </header>

      <div class="px-3 d-flex flex-column gap-4">
        <!-- 対象作品 -->
        <div class="card bg-dark border-0 p-3">
          <div class="mock-tiny text-secondary mb-1">対象作品</div>
          <div class="fw-medium">{{ posterWork ? posterWork.title : '—' }}</div>
          <div v-if="posterWork" class="mock-tiny text-secondary">{{ posterWork.company }} / {{ posterWork.theater }}</div>
        </div>

        <!-- 現在のトップ画像 -->
        <div>
          <label class="form-label mock-tiny text-secondary">現在のトップ画像</label>
          <div v-if="posterWork && posterWork.hasImage" class="mock-poster-current mock-poster-gradient">
            <span class="mock-credit">📷 {{ posterWork.imageBy }}</span>
          </div>
          <div v-else class="mock-poster-current mock-poster-empty-upload">
            <span class="fs-3">🎭</span>
            <span class="small text-secondary">まだ画像がありません</span>
          </div>
        </div>

        <!-- アップロードエリア -->
        <div>
          <label class="form-label mock-tiny text-secondary">新しい画像をアップロード</label>
          <div class="mock-upload-area" role="button">
            <span class="fs-2 text-secondary">📷</span>
            <span class="small text-secondary">タップして写真を選択</span>
          </div>
          <div class="mock-tiny text-secondary mt-2 lh-base">
            この画像は作品ページのトップ画像候補になります。投稿者名も表示されます。
          </div>
        </div>

        <!-- Button -->
        <div class="mb-5">
          <button class="btn mock-btn-primary w-100 fw-medium py-2">送信する</button>
        </div>
      </div>
    </template>

    <!-- ========== BOTTOM NAV ========== -->
    <nav class="mock-bottom-nav">
      <button
        class="mock-nav-btn"
        :class="page === 'top' ? 'mock-color-rose' : 'text-secondary'"
        @click="page = 'top'"
      >
        <span class="mock-nav-icon">🏠</span>
        <span>トップ</span>
      </button>
      <button
        class="mock-nav-btn"
        :class="page === 'work' ? 'mock-color-rose' : 'text-secondary'"
        @click="page = 'work'; selectedWork = selectedWork || works[0]"
      >
        <span class="mock-nav-icon">🎭</span>
        <span>作品</span>
      </button>
      <button
        class="mock-nav-btn"
        :class="page === 'record' ? 'mock-color-rose' : 'text-secondary'"
        @click="page = 'record'"
      >
        <span class="mock-nav-icon">✏️</span>
        <span>記録</span>
      </button>
      <button class="mock-nav-btn text-secondary">
        <span class="mock-nav-icon">👤</span>
        <span>マイページ</span>
      </button>
    </nav>
  </div>
</template>

<style scoped>
/* ---- Shell ---- */
.mock-shell {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  background: #0a0a0b;
  color: #e4e4e7;
  padding-bottom: 5rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* ---- Brand ---- */
.mock-brand {
  letter-spacing: 0.05em;
}

/* ---- Colors ---- */
.mock-color-amber { color: #f59e0b; }
.mock-color-green { color: #34d399; }
.mock-color-rose  { color: #f43f5e; }

/* ---- Badges ---- */
.mock-badge-amber {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  font-weight: 500;
  font-size: 0.65rem;
}
.mock-badge-green {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
  font-weight: 500;
  font-size: 0.65rem;
}
.mock-badge-featured {
  background: #f59e0b;
  color: #000;
  font-weight: 600;
  font-size: 0.65rem;
}

/* ---- Tiny text ---- */
.mock-tiny {
  font-size: 0.7rem;
}

/* ---- Buttons ---- */
.mock-btn-primary {
  background: #e11d48;
  color: #fff;
  border: none;
}
.mock-btn-primary:hover {
  background: #be123c;
  color: #fff;
}
.mock-btn-coupon {
  background: rgba(225, 29, 72, 0.15);
  color: #f43f5e;
  border: none;
  font-size: 0.7rem;
  white-space: nowrap;
}
.mock-btn-status-amber {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}
.mock-btn-status-green {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
  border: 1px solid rgba(52, 211, 153, 0.3);
}

/* ---- Poster card (horizontal scroll) ---- */
.mock-card-sm {
  flex-shrink: 0;
  width: 140px;
}
.mock-poster-sm {
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  padding: 8px;
  overflow: hidden;
}
.mock-poster-gradient {
  background: linear-gradient(135deg, #7c3aed, #c026d3, #e11d48);
}
.mock-poster-empty {
  background: #18181b;
  border: 1px dashed #3f3f46;
  justify-content: center;
  gap: 4px;
}

/* ---- Thumbnail (list cards) ---- */
.mock-thumb {
  width: 56px;
  height: 72px;
  flex-shrink: 0;
  border-radius: 8px;
}
.mock-poster-empty-sm {
  background: #18181b;
  border: 1px dashed #3f3f46;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #52525b;
}

/* ---- Hero (work detail) ---- */
.mock-hero {
  width: 100%;
  aspect-ratio: 4 / 5;
}
.mock-poster-empty-hero {
  width: 100%;
  aspect-ratio: 4 / 5;
  background: #18181b;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.mock-hero-fade {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 6rem;
  background: linear-gradient(transparent, #0a0a0b);
}
.mock-back {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
}

/* ---- Credit ---- */
.mock-credit {
  font-size: 0.6rem;
  color: rgba(255, 255, 255, 0.6);
}

/* ---- Avatar ---- */
.mock-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #27272a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: 600;
}

/* ---- Shop card ---- */
.mock-shop-img {
  width: 100%;
  height: 100px;
  background: linear-gradient(135deg, #27272a 0%, #3f3f46 100%);
}
.mock-shop-img-featured {
  height: 120px;
  background: linear-gradient(135deg, #44403c 0%, #57534e 50%, #44403c 100%);
}
.mock-shop-featured {
  background: #1c1917;
  border: 1px solid rgba(245, 158, 11, 0.25);
}

/* ---- Poster upload ---- */
.mock-poster-current {
  width: 100%;
  aspect-ratio: 3 / 2;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  padding: 12px;
  overflow: hidden;
}
.mock-poster-empty-upload {
  background: #18181b;
  border: 1px dashed #3f3f46;
  justify-content: center;
  gap: 6px;
}
.mock-upload-area {
  width: 100%;
  height: 160px;
  border: 2px dashed #3f3f46;
  border-radius: 12px;
  background: #18181b;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
}
.mock-upload-area:hover {
  border-color: #52525b;
}

/* ---- Bottom nav ---- */
.mock-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  background: rgba(10, 10, 11, 0.95);
  border-top: 1px solid #27272a;
  display: flex;
  justify-content: space-around;
  padding: 0.5rem 0;
  z-index: 100;
  backdrop-filter: blur(8px);
}
.mock-nav-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  background: none;
  border: none;
  font-size: 0.65rem;
  cursor: pointer;
}
.mock-nav-icon {
  font-size: 1.2rem;
}

/* ---- Scroll ---- */
.mock-scroll-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.mock-scroll-hide::-webkit-scrollbar {
  display: none;
}
</style>
