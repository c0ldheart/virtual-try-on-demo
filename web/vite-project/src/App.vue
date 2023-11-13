<script setup lang="ts">
import { NMenu, NButton, NGradientText, NAvatar, NSpin, NImage } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import { h, ref, watch, onMounted } from 'vue'
import { curry, log, unique } from './util'
import Resizable from './Components/Resizable.vue'
import LImg from './Components/LImg.vue'
import ResultImage from './Components/ResultImage.vue'

// TODO: 组件统一导出
// TODO: 优化组件间属性传递
// TODO：图片上传并返回结果
// TODO: Resizable 组件实现默认大小

function handleUpdateValue(key: string, item: MenuOption) {
  log('[onUpdate:value]: ' + JSON.stringify(item))
  type.value = item.key as clothType
  pickedClothID.value = ''
}

// 此处有坑，See https://cn.vitejs.dev/guide/assets.html#new-url-url-import-meta-url
const asset = (path: string) => new URL(`./assets/${path}`, import.meta.url).href
const imgCloth = (id: string) => asset(`clothes/${id}.jpg`)
const imgPreprocessed = (id: string) => asset(`preprocessed/${id}.png`)
const imgTryOn = (clothId: string, humanId: string) => asset(`human/${humanId}/${clothId}_${humanId}.png`)

const humans = unique(Object.keys(import.meta.glob('./assets/human/**')).map(s => s.split('/').at(-2))) as string[]
const humanIndex = ref(0)
const getHuman = (i: number) => humans.at(i % humans.length) as string

const clothes = {
  '未分类': Object.keys(import.meta.glob('./assets/clothes/*')).map(s => s.match(/\/(\w*)\./)?.[1]) as string[]
}
type clothType = keyof typeof clothes

const types = Object.keys(clothes) as clothType[]
const type = ref(types[0])

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
  log('pickCloth', id)
  pickedClothID.value = id
}

const clothHoverStyle = 'hover:border-green-200 hover:border-2 hover:rounded'
const clothPickStyle = 'border-green-400 border-2 rounded'

watch(pickedClothID, (newID: string, oldID: string) => {
  document.querySelectorAll(`[cloth-id="${oldID}"]`).forEach(e => e.className = clothHoverStyle)
  document.querySelectorAll(`[cloth-id="${newID}"]`).forEach(e => e.className = clothPickStyle)
})

</script>

<template>
  <div class="flex flex-col h-screen">
    <div class="flex px-4 pt-4 pb-1 h-[96%]">
      <div class="w-[20%]">
        <n-gradient-text class="text-[2cqw]">寒心霜冻の</n-gradient-text>
        <p class="text-[3cqw] font-bold">虚拟试衣间</p>
        <n-menu class="mt-4" :options="menuOptions" @update:value="handleUpdateValue" :default-value="type" />
      </div>

      <Resizable class="min-w-[30%] max-w-[80%]">
        <div class="flex flex-col h-full overflow-auto" v-for="t of types" v-show="type === t">
          <div class="flex flex-row flex-wrap justify-start">
            <div class="w-1/3 p-1" v-for="item of clothes[type]">
              <button @click="pickCloth(item)">
                <LImg :class="clothHoverStyle" :cloth-id="item" :src="imgCloth(item)" lazy />
              </button>
            </div>
          </div>
        </div>
      </Resizable>

      <div class="flex-1 flex flex-col justify-center items-center">
        <ResultImage class="h-[60%]" @click-left-arrow="humanIndex--" @click-right-arrow="humanIndex++"
          :src="imgTryOn(pickedClothID, getHuman(humanIndex))"></ResultImage>
        <div class="h-[2%]"></div>
        <LImg class="h-[30%]" :src="imgPreprocessed(getHuman(humanIndex))" />
      </div>
    </div>

    <footer class="flex-1 w-full flex justify-center items-center">
      POWERED BY
      <n-gradient-text class="mx-1">
        <a href="https://github.com/c0ldheart" target="_blank">COLDHEART</a>
      </n-gradient-text>
      <n-avatar class="w-4 h-4" src="https://q.qlogo.cn/g?b=qq&nk=630228704&s=100" />
    </footer>
  </div>
</template>
