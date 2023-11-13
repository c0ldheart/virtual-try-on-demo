<script setup lang="ts">
import { ref } from 'vue'
import LImg from './LImg.vue'

const emit = defineEmits(['click-left-arrow', 'click-right-arrow'])
defineProps({
    src: {
        type: String,
        required: true
    }
})

const isImgLoaded = ref(false)

</script>

<template>
    <div class="relative">
        <button v-show="isImgLoaded"
            class="absolute z-10 left-0 flex flex-col justify-center opacity-50 h-full cursor-pointer toggle-human"
            @click="$emit('click-left-arrow')">
            <svg xmlns="http://www.w3.org/2000/svg" height="10%" viewBox="0 0 24 24">
                <path d="M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z"></path>
            </svg>
        </button>
        <button v-show="isImgLoaded"
            class="absolute z-10 right-0 flex flex-col justify-center opacity-50 h-full cursor-pointer toggle-human"
            @click="$emit('click-right-arrow')">
            <svg xmlns="http://www.w3.org/2000/svg" height="10%" viewBox="0 0 24 24">
                <path d="M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z"></path>
            </svg>
        </button>
        <LImg class="h-full" :src="src" @load-success="isImgLoaded = true" />
    </div>
</template>
