<script setup>
const props = defineProps({
  src: { type: String, default: null },
  name: { type: String, default: '' },
  size: { type: Number, default: 40 },
})

const initial = props.name ? props.name.charAt(0).toUpperCase() : '?'
</script>

<template>
  <div class="user-avatar" :style="{ width: size + 'px', height: size + 'px', fontSize: (size * 0.4) + 'px' }">
    <img v-if="src" :src="src" :alt="name" />
    <span v-else>{{ initial }}</span>
  </div>
</template>

<style scoped>
.user-avatar {
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: black;
  flex-shrink: 0;
  overflow: hidden;
  line-height: 1;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}
</style>
