<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: true
  }
})

const isVisible = ref(true)

watch(() => props.show, (newVal) => {
  if (!newVal) {
    // フェードアウト開始、0.5秒後にDOM削除
    setTimeout(() => {
      isVisible.value = false
    }, 500)
  } else {
    isVisible.value = true
  }
})
</script>

<template>
  <div
    v-if="isVisible"
    class="wrapper pt-5"
    :class="{ 'wrapper--fadeout': !show }"
    style="min-height: 80vh;">
    <div class="loader"></div>
  </div>
</template>


<style scoped>
.wrapper {
  opacity: 1;
  transition: opacity 0.5s ease-out;
}

.wrapper--fadeout {
  opacity: 0;
}

/* HTML: <div class="loader"></div> */
.loader {
  width: 40px;
  aspect-ratio: 1;
  border-radius: 50%;
  border: 5px solid #000000;
  animation:
    l20-1 0.8s infinite linear alternate,
    l20-2 1.6s infinite linear;
}
@keyframes l20-1{
   0%    {clip-path: polygon(50% 50%,0       0,  50%   0%,  50%    0%, 50%    0%, 50%    0%, 50%    0% )}
   12.5% {clip-path: polygon(50% 50%,0       0,  50%   0%,  100%   0%, 100%   0%, 100%   0%, 100%   0% )}
   25%   {clip-path: polygon(50% 50%,0       0,  50%   0%,  100%   0%, 100% 100%, 100% 100%, 100% 100% )}
   50%   {clip-path: polygon(50% 50%,0       0,  50%   0%,  100%   0%, 100% 100%, 50%  100%, 0%   100% )}
   62.5% {clip-path: polygon(50% 50%,100%    0, 100%   0%,  100%   0%, 100% 100%, 50%  100%, 0%   100% )}
   75%   {clip-path: polygon(50% 50%,100% 100%, 100% 100%,  100% 100%, 100% 100%, 50%  100%, 0%   100% )}
   100%  {clip-path: polygon(50% 50%,50%  100%,  50% 100%,   50% 100%,  50% 100%, 50%  100%, 0%   100% )}
}
@keyframes l20-2{ 
  0%    {transform:scaleY(1)  rotate(0deg)}
  49.99%{transform:scaleY(1)  rotate(135deg)}
  50%   {transform:scaleY(-1) rotate(0deg)}
  100%  {transform:scaleY(-1) rotate(-135deg)}
}
</style>