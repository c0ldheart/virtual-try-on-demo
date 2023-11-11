<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NSpin } from 'naive-ui'

const isLoadding = ref(true)

function loaded() {
    isLoadding.value = false
}

function load() {
    isLoadding.value = true
}

const img = ref(null)

const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'src') {
            load()
        }
    })
})

onMounted(() => {
    observer.observe(img.value as unknown as Node, { attributes: true, attributeFilter: ['src'] })
})

</script>

<template>
    <div class="flex justify-center relative -z-10">
        <img id="img" ref="img" class="h-full" @load="loaded" @error="loaded" v-bind="$attrs">
        <n-spin class="absolute h-full w-full" v-show="isLoadding"></n-spin>
    </div>
</template>
