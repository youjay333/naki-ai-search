<script setup>
import { Search, Sparkles } from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  loading: {
    type: Boolean,
    default: false,
  },
  compact: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'submit'])

function updateValue(event) {
  emit('update:modelValue', event.target.value)
}

function submit() {
  if (!props.loading && props.modelValue.trim()) {
    emit('submit')
  }
}
</script>

<template>
  <form class="search-box" :class="{ compact }" @submit.prevent="submit">
    <label class="visually-hidden" for="question-input">搜索问题</label>
    <Search class="search-icon" :size="22" aria-hidden="true" />
    <textarea
      id="question-input"
      :value="modelValue"
      rows="1"
      placeholder="向 naki 提问，搜索最新信息..."
      :disabled="loading"
      @input="updateValue"
      @keydown.enter.exact.prevent="submit"
    />
    <button type="submit" :disabled="loading || !modelValue.trim()" title="开始 AI 搜索">
      <Sparkles :size="18" aria-hidden="true" />
      <span>{{ loading ? '搜索中' : '搜索' }}</span>
    </button>
  </form>
</template>
