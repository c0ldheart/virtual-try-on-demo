<script setup lang="ts">
import { NMenu, NButton, NImage, NGradientText, NAvatar } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import { h, ref } from 'vue'
import { curry } from './util'
function handleUpdateValue(key: string, item: MenuOption) {
  console.log('[onUpdate:value]: ' + JSON.stringify(item))
  type.value = item.key as clothType
  pickedClothID.value = ''
}

const img = (type: 'cloth' | 'human', id: string) => `https://raw.githubusercontent.com/c0ldheart/virtual-try-on-demo/master/assert/${type}/${id}.jpg`
const imgCloth: (id: string) => string = curry(img)('cloth')
const imgHuman: (id: string) => string = curry(img)('human')

const clothes = {
  'T恤': ['00013_00', '00013_00', '00013_00', '00013_00'],
  '不知道叫啥分类': ['00008_00', '00008_00', '00008_00', '00008_00',]
}
type clothType = keyof typeof clothes

const types = Object.keys(clothes) as clothType[]
let type = ref<clothType>('T恤')

const menuOptions: MenuOption[] = [
  {
    key: 'divider',
    type: 'divider',
  },
  ...types.map(e => ({
    label: () => h('p', {
      style: 'font-size: 1.5cqw'
    }, e), key: e
  }))
]

const pickedClothID = ref('')
function pickCloth(id: string) {
  console.log('pickCloth', id)
  pickedClothID.value = id
}

</script>

<template>
  <div class="p-4 flex h-screen overflow-hidden">
    <div class="w-1/5">
      <n-gradient-text style="font-size: 2cqw;">寒心霜冻の</n-gradient-text>
      <p class="font-bold" style="font-size: 3cqw;">虚拟试衣间</p>
      <n-menu class="mt-4" :options="menuOptions" @update:value="handleUpdateValue" :default-value="type" />
      <!-- <n-button @click="console.log(type)">debug</n-button> -->
    </div>

    <div class="w-3/5 flex flex-col overflow-auto" style="height: 96%;" v-for="t of types"
      v-show="type === t">
      <div class="flex flex-row flex-wrap justify-start">
        <div class="w-1/3 p-2" v-for="item of clothes[type]">
          <button @click="pickCloth(item)">
            <img :alt="imgCloth(item)" :src="imgCloth(item)" loading="lazy" />
          </button>
        </div>
      </div>
    </div>

    <div class="w-1/5 flex justify-center items-center">
      <div v-show="pickedClothID">
        <img :src="imgHuman(pickedClothID)" />
      </div>
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
