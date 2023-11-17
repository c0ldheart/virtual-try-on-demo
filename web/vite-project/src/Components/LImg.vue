<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NSpin } from 'naive-ui'

defineProps({
    src: {
        type: String,
        required: true
    },
    lazy: Boolean,
})
const emit = defineEmits(['load-success'])

const isLoadding = ref(true)

function loaded() {
    isLoadding.value = false
}

function load() {
    isLoadding.value = true
}

function loadSuccess() {
    loaded()
    emit('load-success')
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
    <div class="flex justify-center relative">
        <img ref="img" class="h-full w-full" @load="loadSuccess" @error="loaded" :src="src"
            :loading="lazy ? 'lazy' : 'eager'">
        <n-spin class="absolute h-full w-full" v-show="isLoadding"></n-spin>
    </div>
</template>
