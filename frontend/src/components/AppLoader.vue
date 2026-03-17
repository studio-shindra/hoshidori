<template>
  <div class="d-flex justify-content-center align-items-center py-4">
    <div class="app-spinner" />
  </div>
</template>

<style scoped>
.app-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #f43f5e;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
