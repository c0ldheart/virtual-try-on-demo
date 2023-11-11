<script setup lang="ts">
import { ref } from 'vue'
import { NSpin } from 'naive-ui'

const isImageLoaded = ref(false)
</script>

<template>
    <div class="flex justify-center">
        <img class="h-full" v-show="isImageLoaded" @load="isImageLoaded = true" v-bind="$attrs">
        <n-spin v-show="!isImageLoaded"></n-spin>
    </div>
</template>
