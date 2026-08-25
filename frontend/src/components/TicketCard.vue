<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { IconCalendarEvent, IconMapPin, IconSparkles, IconStarFilled } from '@tabler/icons-vue'

const props = defineProps({
  workTitle: { type: String, default: '' },
  workSlug: { type: String, default: null },
  date: { type: String, default: '' },
  time: { type: String, default: '' },
  theaterName: { type: String, default: '' },
  theaterArea: { type: String, default: '' },
  status: { type: String, default: 'planned' },
  afterShopName: { type: String, default: '' },
  compact: { type: Boolean, default: false },
})

const dateParts = computed(() => {
  if (!props.date) return { month: '--', day: '--', weekday: '' }
  const d = new Date(`${props.date}T00:00:00`)
  if (Number.isNaN(d.getTime())) return { month: '--', day: '--', weekday: '' }
  return {
    month: `${d.getMonth() + 1}月`,
    day: String(d.getDate()).padStart(2, '0'),
    weekday: ['日', '月', '火', '水', '木', '金', '土'][d.getDay()],
  }
})

const statusLabel = computed(() => props.status === 'watched' ? '観た' : '観る')
</script>

<template>
  <component
    :is="workSlug ? RouterLink : 'div'"
    :to="workSlug ? `/works/${workSlug}` : undefined"
    class="hoshidori-ticket text-decoration-none text-white"
    :class="[{ compact }, `status-${status}`]"
  >
    <div class="ticket-date">
      <span class="ticket-month">{{ dateParts.month }}</span>
      <strong>{{ dateParts.day }}</strong>
      <span>{{ dateParts.weekday }}</span>
    </div>
    <div class="ticket-cut" aria-hidden="true"></div>
    <div class="ticket-main min-w-0">
      <div class="d-flex align-items-center gap-1 ticket-status">
        <IconStarFilled v-if="status === 'watched'" :size="11" />
        <IconCalendarEvent v-else :size="12" />
        {{ statusLabel }}<span v-if="time">・{{ time.slice(0, 5) }}</span>
      </div>
      <div class="ticket-title text-truncate">{{ workTitle }}</div>
      <div v-if="theaterName" class="ticket-meta text-truncate">
        <IconMapPin :size="12" />{{ theaterName }}<span v-if="theaterArea">・{{ theaterArea }}</span>
      </div>
      <div v-if="afterShopName" class="ticket-after text-truncate">
        <IconSparkles :size="12" />感想戦：{{ afterShopName }}
      </div>
    </div>
  </component>
</template>

<style scoped>
.hoshidori-ticket {
  position: relative;
  display: grid;
  grid-template-columns: 68px 1px minmax(0, 1fr);
  min-height: 112px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  background:
    radial-gradient(circle at 92% 12%, rgba(244, 63, 94, 0.2), transparent 30%),
    linear-gradient(135deg, #202026, #121216);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.22);
}
.hoshidori-ticket:hover { color: #fff; border-color: rgba(255, 255, 255, 0.24); }
.hoshidori-ticket.status-watched {
  background:
    radial-gradient(circle at 92% 12%, rgba(245, 158, 11, 0.18), transparent 30%),
    linear-gradient(135deg, #202026, #121216);
}
.ticket-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #d4d4d8;
  font-size: 0.7rem;
  line-height: 1.1;
}
.ticket-date strong { color: #fff; font-size: 1.75rem; letter-spacing: -0.08em; }
.ticket-month { color: #fda4af; font-weight: 700; }
.status-watched .ticket-month { color: #fbbf24; }
.ticket-cut { border-left: 1px dashed rgba(255, 255, 255, 0.22); margin: 12px 0; }
.ticket-main { display: flex; flex-direction: column; justify-content: center; gap: 5px; padding: 14px 16px; }
.ticket-status { color: #a1a1aa; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.05em; }
.ticket-title { font-size: 1rem; font-weight: 800; }
.ticket-meta, .ticket-after { display: flex; align-items: center; gap: 3px; color: #a1a1aa; font-size: 0.72rem; }
.ticket-after { color: #fda4af; }
.compact { min-height: 92px; }
.compact .ticket-main { padding-top: 10px; padding-bottom: 10px; }
</style>
