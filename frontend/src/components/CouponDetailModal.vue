<script setup>
import { IconTicket, IconAlertCircle, IconQrcode } from '@tabler/icons-vue'

defineProps({
  coupon: { type: Object, default: null },
  shopName: { type: String, default: '' },
})

const emit = defineEmits(['close', 'use'])
</script>

<template>
  <Teleport to="body">
    <div v-if="coupon" class="modal-backdrop text-black" @click.self="emit('close')">
      <div class="coupon-modal">
        <!-- Ticket top edge -->
        <div class="coupon-edge"></div>

        <div class="coupon-body">
          <!-- Header -->
          <div class="text-center mb-1">
            <div class="small mb-1">{{ shopName }}</div>
            <div class="fs-5 fw-bold color-rose">{{ coupon.title }}</div>
          </div>

          <!-- Discount -->
          <div v-if="coupon.discount_text" class="text-center mb-3 w-100">
            <div class="fs-3 fw-bold bg-rose text-white px-2 py-1 w-100 rounded">{{ coupon.discount_text }}</div>
          </div>

          <!-- Dashed divider -->
          <div class="coupon-divider"></div>

          <!-- Description -->
          <p v-if="coupon.description" class="small lh-base mt-3">{{ coupon.description }}</p>

          <!-- Conditions -->
          <div v-if="coupon.conditions" class="mt-3">
            <div class="small fw-semibold mb-1 badge bg-dark">利用条件</div>
            <p class="small lh-base mb-0 whitespace-pre-line">{{ coupon.conditions }}</p>
          </div>

          <!-- Validity -->
          <div v-if="coupon.start_date || coupon.end_date" class="mt-3">
            <div class="small fw-semibold mb-1 badge bg-dark">有効期間</div>
            <p class="small mb-0">
              <template v-if="coupon.start_date && coupon.end_date">{{ coupon.start_date }} 〜 {{ coupon.end_date }}</template>
              <template v-else-if="coupon.end_date">{{ coupon.end_date }} まで</template>
              <template v-else>{{ coupon.start_date }} から</template>
            </p>
          </div>

          <!-- Future: QR display -->
          <div v-if="coupon.display_type === 'qr'" class="mt-3 text-center py-4 border border-dashed border-secondary rounded-3">
            <IconQrcode :size="48" class="" />
            <div class="small  mt-1">QRコード</div>
          </div>

          <div class="d-flex align-items-start gap-1 mt-3">
            <IconAlertCircle :size="12" class=" mt-1 flex-shrink-0" />
            <span class="tiny lh-sm">クーポンの利用は店舗スタッフにこの画面をご提示ください。</span>
          </div>
        </div>

        <!-- Ticket bottom edge -->
        <div class="coupon-edge"></div>

        <!-- Close -->
        <button class="btn btn-link text-white fw-bold small text-decoration-none" @click="emit('close')">閉じる</button>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  z-index: 1060;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.coupon-modal {
  width: 100%;
  max-width: 380px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.coupon-edge {
  width: 100%;
  height: 12px;
  background: radial-gradient(circle at 12px 12px, transparent 10px, #1c1c1c 10px) repeat-x;
  background-size: 24px 12px;
}

.coupon-body {
  background: white;
  padding: 1.5rem;
  width: 100%;
  border-left: 2px dashed #3f3f46;
  border-right: 2px dashed #3f3f46;
}

.coupon-divider {
  border-top: 2px dashed #3f3f46;
  margin: 0 -1.5rem;
  padding: 0 1.5rem;
}

.whitespace-pre-line {
  white-space: pre-line;
}
</style>
