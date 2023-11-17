<script setup lang="ts">
import { NMenu, NButton, NGradientText, NAvatar, NSpin, NImage, createDiscreteApi, NTooltip } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import { h, ref, watch, onMounted, nextTick, triggerRef, computed } from 'vue'
import { curry, log, unique, isBlobUrl } from './util'
import { Resizable, LImg, ResultImage } from './Components'

const { message } = createDiscreteApi(['message'])

// TODO: 优化组件间属性传递
// TODO: Resizable 组件实现默认大小

function handleUpdateValue(key: string, item: MenuOption) {
  log('[onUpdate:value]: ' + JSON.stringify(item))
  type.value = item.key as clothType
  pickedClothID.value = ''
}

const resultMap: { [key: string]: string } = {}
const buildKey = (a: string, b: string) => a + '---' + b

const preprocessMap: { [key: string]: string } = {}

// 此处有坑，See https://cn.vitejs.dev/guide/assets.html#new-url-url-import-meta-url
const asset = (path: string) => new URL(`./assets/${path}`, import.meta.url).href
const imgCloth = (id: string) => asset(`clothes/${id}.jpg`)

const imgPreprocessed = (human: string) =>
  isBlobUrl(human)
    ? preprocessMap[human] ?? ''
    : asset(`preprocessed/${human}.png`)

const imgTryOn = (clothId: string, human: string) =>
  isBlobUrl(human)
    ? (resultMap[buildKey(human, pickedClothID.value)] ?? human)
    : asset(`human/${human}/${clothId}_${human}.png`)

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

const pickedClothID = ref(import.meta.env.DEV ? '5' : '')
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

const selectFile = ref<HTMLInputElement | null>(null)

function handleFileSelect(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (files) {
    const file = files[0]
    const blobUrl = URL.createObjectURL(file)
    log(blobUrl)

    humans.push(blobUrl)
    humanIndex.value = humans.length - 1
    log(humans)

    message.success('已选择文件：' + file.name)
  }
}

async function handleFileUpload() {
  const human = getHuman(humanIndex.value)

  const formData = new FormData()
  const humanImage = await (await fetch(human)).blob()
  formData.append('humanImage', humanImage)
  formData.append('clothId', pickedClothID.value)

  const res = await fetch('http://localhost:6001/tryon', {
    method: 'POST',
    body: formData,
  })
  const resultBlob = await res.blob()
  const resultBlobUrl = URL.createObjectURL(resultBlob)
  resultMap[buildKey(human, pickedClothID.value)] = resultBlobUrl

  triggerRef(humanIndex)

  log('res:' + resultBlobUrl)
  log(resultMap)
}

const tryonConditions: [() => boolean, string][] = [
  [() => pickedClothID.value === '', '请选择一件衣服'],
  [() => !isBlobUrl(getHuman(humanIndex.value)), '请选择自己上传的图片'],
]

const tryonButtonTooltip = computed(() => tryonConditions.filter(([f]) => f()).map(([_, s]) => s))
const isTryonButtonUsable = computed(() => tryonButtonTooltip.value.length === 0)

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
        <div class="h-[30%] w-[80%] flex justify-center items-center">
          <LImg v-if="imgPreprocessed(getHuman(humanIndex))" :src="imgPreprocessed(getHuman(humanIndex))" />
          <p v-else>暂无预处理图片</p>
        </div>
        <div class="h-[2%]"></div>
        <div class="flex justify-center items-center">
          <input ref="selectFile" type="file" @change="handleFileSelect" hidden />
          <n-button class="mx-2" @click="selectFile?.click()">选择图片</n-button>
          <n-space><n-tooltip trigger="hover" :disabled="isTryonButtonUsable">
              <template #trigger>
                <n-button class="bg-emerald-500" @click="handleFileUpload"
                  :type="isTryonButtonUsable ? 'success' : undefined" :disabled="!isTryonButtonUsable">
                  Try On!
                </n-button>
              </template>
              <p v-for="message of tryonButtonTooltip">{{ message }}</p>
            </n-tooltip></n-space>
        </div>
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
