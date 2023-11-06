<script setup lang="ts">
</script>

<template>
  <div class="relative">
    <div class="resize"></div>
    <div class="line opacity-20"></div>
    <div class="content absolute">
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.resize {
  position: relative;
  transform: scaleY(100);
  overflow: scroll;
  resize: horizontal;
  opacity: 0;
  cursor: ew-resize;
  min-width: 100%;
  max-width: 100%;
}

.line {
  position: absolute;
  top: 0;
  right: 0;
  width: 5px;
  bottom: 0;
  background-color: royalblue;
  transition: .3s;
  pointer-events: none;
}

.content {
  top: 0;
  right: 5px;
  bottom: 0;
  left: 0;
}
</style>
