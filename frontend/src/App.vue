<script setup>
import { computed, ref } from 'vue'
import { Clock, ExternalLink, FileText, LoaderCircle, RotateCcw, X } from 'lucide-vue-next'
import MarkdownBlock from './components/MarkdownBlock.vue'
import SearchBox from './components/SearchBox.vue'
import { addHistoryItem, loadHistory, saveHistory } from './utils/history'
import { streamSearch } from './utils/sse'

const query = ref('')
const currentQuery = ref('')
const answer = ref('')
const results = ref([])
const relatedQuestions = ref([])
const statusMessage = ref('')
const errorMessage = ref('')
const loading = ref(false)
const history = ref(loadHistory())
const abortController = ref(null)

const hasResultView = computed(() => loading.value || answer.value || results.value.length > 0 || errorMessage.value)
const citedSourceIds = computed(() => {
  const matches = answer.value.match(/\[(\d+)\]/g) || []
  return new Set(matches.map((item) => Number(item.replace(/\D/g, ''))))
})

async function submitSearch(nextQuery = query.value) {
  const trimmed = nextQuery.trim()
  if (!trimmed || loading.value) return

  abortController.value?.abort()
  abortController.value = new AbortController()
  query.value = trimmed
  currentQuery.value = trimmed
  answer.value = ''
  results.value = []
  relatedQuestions.value = []
  errorMessage.value = ''
  statusMessage.value = '准备搜索'
  loading.value = true
  history.value = addHistoryItem(history.value, trimmed)
  saveHistory(history.value)

  try {
    await streamSearch({
      query: trimmed,
      maxResults: 8,
      signal: abortController.value.signal,
      onEvent({ event, data }) {
        if (event === 'status') statusMessage.value = data.message
        if (event === 'results') results.value = data.results || []
        if (event === 'token') answer.value += data.text || ''
        if (event === 'related') relatedQuestions.value = data.questions || []
        if (event === 'error') throw new Error(data.message || '搜索失败')
        if (event === 'done') {
          if (data.answer) answer.value = data.answer
          statusMessage.value = '完成'
        }
      },
    })
  } catch (error) {
    if (error.name !== 'AbortError') {
      errorMessage.value = error.message || '搜索失败，请稍后重试'
    }
  } finally {
    loading.value = false
    abortController.value = null
  }
}

function stopSearch() {
  abortController.value?.abort()
  loading.value = false
  statusMessage.value = '已停止'
}

function clearHistory() {
  history.value = []
  saveHistory([])
}
</script>

<template>
  <main class="app-shell" :class="{ 'result-mode': hasResultView }">
    <header class="topbar">
      <button class="brand" type="button" @click="submitSearch('今天有什么值得关注的科技新闻？')">
        <span class="brand-mark">N</span>
        <span>naki-ai-search</span>
      </button>
      <button v-if="loading" class="ghost-button" type="button" @click="stopSearch">
        <X :size="17" aria-hidden="true" />
        <span>停止</span>
      </button>
    </header>

    <section v-if="!hasResultView" class="home-view">
      <div class="home-copy">
        <p class="eyebrow">AI Web Search</p>
        <h1>搜索最新信息，再交给 AI 综合判断。</h1>
      </div>
      <SearchBox v-model="query" :loading="loading" @submit="submitSearch()" />

      <div v-if="history.length" class="history-panel">
        <div class="panel-heading">
          <span>搜索历史</span>
          <button type="button" @click="clearHistory">清空</button>
        </div>
        <div class="history-list">
          <button v-for="item in history" :key="item.createdAt" type="button" @click="submitSearch(item.query)">
            <Clock :size="15" aria-hidden="true" />
            <span>{{ item.query }}</span>
          </button>
        </div>
      </div>
    </section>

    <section v-else class="results-view">
      <div class="sticky-search">
        <SearchBox v-model="query" compact :loading="loading" @submit="submitSearch()" />
      </div>

      <div class="content-grid">
        <article class="answer-panel">
          <div class="section-title">
            <div>
              <p>AI 综合回答</p>
              <h2>{{ currentQuery }}</h2>
            </div>
            <div v-if="loading" class="status">
              <LoaderCircle :size="17" aria-hidden="true" />
              <span>{{ statusMessage }}</span>
            </div>
          </div>

          <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
          <MarkdownBlock v-else :content="answer || (loading ? '正在整理搜索结果...' : '')" />

          <div v-if="relatedQuestions.length" class="related">
            <h3>继续探索</h3>
            <button v-for="question in relatedQuestions" :key="question" type="button" @click="submitSearch(question)">
              <RotateCcw :size="15" aria-hidden="true" />
              <span>{{ question }}</span>
            </button>
          </div>
        </article>

        <aside class="sources-panel">
          <div class="section-title compact-title">
            <div>
              <p>引用来源</p>
              <h2>{{ citedSourceIds.size || 0 }} 个已引用</h2>
            </div>
          </div>
          <a
            v-for="item in results.filter((result) => citedSourceIds.has(result.id))"
            :key="`cited-${item.id}`"
            class="source-item cited"
            :href="item.url"
            target="_blank"
            rel="noreferrer"
          >
            <span>[{{ item.id }}]</span>
            <strong>{{ item.title }}</strong>
            <ExternalLink :size="15" aria-hidden="true" />
          </a>

          <div class="section-title compact-title all-results-title">
            <div>
              <p>完整结果</p>
              <h2>{{ results.length }} 条网页</h2>
            </div>
          </div>
          <a
            v-for="item in results"
            :key="item.id"
            class="result-item"
            :href="item.url"
            target="_blank"
            rel="noreferrer"
          >
            <div class="result-rank">
              <FileText :size="16" aria-hidden="true" />
              <span>{{ item.id }}</span>
            </div>
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.content }}</p>
              <small>{{ item.url }}</small>
            </div>
          </a>
        </aside>
      </div>
    </section>
  </main>
</template>
