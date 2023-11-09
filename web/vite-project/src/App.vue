<script setup lang="ts">
import { NMenu, NButton, NImage, NGradientText, NAvatar } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import { h, ref, watch, onMounted } from 'vue'
import { curry } from './util'
import Resizable from './Components/Resizable.vue'

function handleUpdateValue(key: string, item: MenuOption) {
  console.log('[onUpdate:value]: ' + JSON.stringify(item))
  type.value = item.key as clothType
  pickedClothID.value = ''
}

const img = (type: 'clothes' | 'human', id: string) => `https://raw.githubusercontent.com/c0ldheart/virtual-try-on-demo/master/asset/${type}/${id}.jpg`
const imgCloth: (id: string) => string = curry(img)('clothes')
const imgPreprocessed = (id: string) => `src/assets/preprocessed/${id}.png`

const clothes = {
  'T恤': Array.from({ length: 50 }, (_, i) => (i + 1).toString()),
  '不知道叫啥分类': Array.from({ length: 50 }, (_, i) => (i + 1).toString()),
}
type clothType = keyof typeof clothes

const types = Object.keys(clothes) as clothType[]
const type = ref<clothType>(types[0])

const menuOptions: MenuOption[] = [
  {
    key: 'divider',
    type: 'divider',
  },
  ...types.map(e => ({
    label: () => h('p', {
      class: 'text-[1.5cqw]'
    }, e), key: e
  }))
]

const pickedClothID = ref('')
function pickCloth(id: string) {
  console.log('pickCloth', id)
  pickedClothID.value = id
}

const clothHoverStyle = 'hover:border-green-200 hover:border-2 hover:rounded'
const clothPickStyle = 'border-green-400 border-2 rounded'

watch(pickedClothID, (newID: string, oldID: string) => {
  document.querySelectorAll(`[cloth-id="${oldID}"]`).forEach(e => e.className = clothHoverStyle)
  document.querySelectorAll(`[cloth-id="${newID}"]`).forEach(e => e.className = clothPickStyle)
})

const humans = ['2297f5f5', '2397f788']
const humanIndex = ref(0)
const getHuman = (i: number) => humans.at(i % humans.length) as string
const imgTryOn = (clothId: string, humanId: string) => `https://raw.githubusercontent.com/c0ldheart/virtual-try-on-demo/master/asset/human/${humanId}/${clothId}_${humanId}.png`
</script>

<template>
  <div class="p-4 flex h-screen overflow-hidden">
    <div class="w-[20%]">
      <n-gradient-text class="text-[2cqw]">寒心霜冻の</n-gradient-text>
      <p class="text-[3cqw] font-bold">虚拟试衣间</p>
      <n-menu class="mt-4" :options="menuOptions" @update:value="handleUpdateValue" :default-value="type" />
      <!-- <n-button @click="console.log(type)">debug</n-button> -->
    </div>

    <Resizable class="min-w-[30%] max-w-[80%]">
      <div class=" h-[96%] flex flex-col overflow-auto" v-for="t of types" v-show="type === t">
        <div class="flex flex-row flex-wrap justify-start">
          <div class="w-1/3 p-1" v-for="item of clothes[type]">
            <button @click="pickCloth(item)">
              <img :class="clothHoverStyle" :cloth-id="item" :alt="imgCloth(item)" :src="imgCloth(item)" loading="lazy" />
            </button>
          </div>
        </div>
      </div>
    </Resizable>

    <div class="flex-1 flex flex-col justify-center items-center h-[96%]" v-show="pickedClothID">
      <div class="relative">
        <button class="absolute left-0 flex flex-col justify-center opacity-50 h-full cursor-pointer"
          @click="humanIndex--">
          <svg xmlns="http://www.w3.org/2000/svg" height="10%" viewBox="0 0 24 24">
            <path d="M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z"></path>
          </svg>
        </button>
        <button class="absolute right-0 flex flex-col justify-center opacity-50 h-full cursor-pointer"
          @click="humanIndex++">
          <svg xmlns="http://www.w3.org/2000/svg" height="10%" viewBox="0 0 24 24">
            <path d="M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z"></path>
          </svg>
        </button>
        <img class="max-h-[60vh]" :src="pickedClothID ? imgTryOn(pickedClothID, getHuman(humanIndex)) : ''" />
      </div>
      <div class="h-[2%]"></div>
      <img class=" max-h-[30%]" :src="pickedClothID ? imgPreprocessed(getHuman(humanIndex)) : ''">
    </div>
  </div>

  <footer class="text-center fixed bottom-1 w-full flex justify-center items-center">
    POWERED BY
    <n-gradient-text class="mx-1">
      <a href="https://github.com/c0ldheart" target="_blank">COLDHEART</a>
    </n-gradient-text>
    <n-avatar class="w-4 h-4" src="https://q.qlogo.cn/g?b=qq&nk=630228704&s=100" />
  </footer>
</template>
