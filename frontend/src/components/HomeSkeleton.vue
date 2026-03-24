<template>
  <div>
    <!-- これから観る -->
    <section class="mb-4">
      <div class="skeleton-text mb-3" style="width: 120px; height: 24px"></div>
      <div class="d-flex gap-2 overflow-hidden">
        <div v-for="i in 3" :key="'p'+i" class="skeleton flex-shrink-0" style="width: 200px; aspect-ratio: 3/4; border-radius: 8px"></div>
      </div>
    </section>

    <!-- 観た -->
    <section class="mb-4">
      <div class="skeleton-text mb-3" style="width: 100px; height: 24px"></div>
      <div class="d-flex flex-column gap-2">
        <div v-for="i in 3" :key="'w'+i" class="d-flex gap-2 align-items-center">
          <div class="skeleton flex-shrink-0" style="width: 72px; height: 96px; border-radius: 6px"></div>
          <div class="flex-grow-1 d-flex flex-column gap-2">
            <div class="skeleton-text" style="width: 70%"></div>
            <div class="skeleton-text-sm" style="width: 50%"></div>
            <div class="skeleton-text-sm" style="width: 40%"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- お店セクション -->
    <section class="mb-4">
      <div class="skeleton-text mb-3" style="width: 160px; height: 24px"></div>
      <div class="d-flex gap-2 overflow-hidden">
        <div v-for="i in 3" :key="'s'+i" class="flex-shrink-0" style="width: 200px">
          <div class="skeleton" style="width: 100%; aspect-ratio: 16/9; border-radius: 8px 8px 0 0"></div>
          <div class="skeleton d-flex flex-column gap-2 p-3" style="border-radius: 0 0 8px 8px">
            <div class="skeleton-text" style="width: 80%"></div>
            <div class="skeleton-text-sm" style="width: 60%"></div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
