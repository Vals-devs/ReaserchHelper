<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'
import { useAIStore } from '@/stores/ai'
import { useCollectionsStore } from '@/stores/collections'

interface Paper {
  id: string
  external_id: string
  source: string
  title: string
  authors: string[]
  abstract: string | null
  full_text: string | null
  year: number | null
  doi: string | null
  url: string | null
  citation_count: number
  fields_of_study: string[]
  page_count: number | null
}

const route = useRoute()
const router = useRouter()
const aiStore = useAIStore()
const collectionsStore = useCollectionsStore()

const paper = ref<Paper | null>(null)
const loading = ref(true)
const error = ref('')
const relatedPapers = ref<any[]>([])
const loadingRelated = ref(false)
const summaryOpen = ref(false)
const activeAiTab = ref<'summary' | 'chat' | 'explain'>('summary')

// Explain text state
const explainText = ref('')
const explainResult = ref('')
const explainLoading = ref(false)

// Chat state
const chatQuery = ref('')
const chatMessages = ref<{ role: 'user' | 'assistant', content: string }[]>([])
const chatLoading = ref(false)
const chatError = ref('')

async function sendChatMessage() {
  if (!chatQuery.value.trim() || chatLoading.value || !paper.value) return
  
  const userText = chatQuery.value.trim()
  chatQuery.value = ''
  chatError.value = ''
  
  chatMessages.value.push({ role: 'user', content: userText })
  chatLoading.value = true
  
  try {
    const { data } = await api.post('/ai/chat', {
      paper_id: paper.value.id,
      messages: chatMessages.value
    })
    chatMessages.value.push({ role: 'assistant', content: data.reply })
  } catch (err: any) {
    chatError.value = err.response?.data?.detail || 'Gagal mengirim pesan ke AI'
  } finally {
    chatLoading.value = false
  }
}

// Translate abstract state
const translatedAbstract = ref('')
const translatingAbstract = ref(false)

// Save to collection state
const showSaveModal = ref(false)
const saveSuccess = ref('')
const saveError = ref('')
const newCollectionName = ref('')
const savingToCollection = ref(false)

const paperId = route.params.id as string

onMounted(async () => {
  await fetchPaper()
  await collectionsStore.fetchCollections()
})

async function fetchPaper() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/papers/${paperId}`)
    paper.value = data
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Gagal memuat detail paper'
  } finally {
    loading.value = false
  }
}

async function fetchRelated() {
  loadingRelated.value = true
  relatedPapers.value = []
  try {
    const { data } = await api.get(`/papers/${paperId}/related`)
    relatedPapers.value = data.related || []
  } catch (err: any) {
    console.error('Failed to fetch related papers:', err)
    relatedPapers.value = []
  } finally {
    loadingRelated.value = false
  }
}

async function translateAbstract() {
  if (!paper.value?.abstract) return
  translatingAbstract.value = true
  translatedAbstract.value = ''
  try {
    const { data } = await api.post('/ai/translate', {
      text: paper.value.abstract,
      target_language: 'id',
    })
    translatedAbstract.value = data.translation
  } catch {
    translatedAbstract.value = 'Gagal menerjemahkan abstrak. Coba lagi.'
  } finally {
    translatingAbstract.value = false
  }
}

async function handleSummarize() {
  if (!paper.value) return
  summaryOpen.value = true
  activeAiTab.value = 'summary'
  await aiStore.summarize(paper.value.id)
}

async function handleExplain() {
  if (!explainText.value.trim()) return
  explainLoading.value = true
  explainResult.value = ''
  try {
    await aiStore.explain(explainText.value, 'id')
    explainResult.value = aiStore.explanation
  } catch {
    explainResult.value = 'Gagal menjelaskan teks. Coba lagi.'
  } finally {
    explainLoading.value = false
  }
}

async function saveToCollection(collectionId: string) {
  if (!paper.value) return
  savingToCollection.value = true
  saveError.value = ''
  saveSuccess.value = ''
  try {
    await api.post(`/collections/${collectionId}/papers`, { paper_id: paper.value.id })
    saveSuccess.value = 'Paper berhasil ditambahkan ke koleksi!'
    showSaveModal.value = false
    setTimeout(() => { saveSuccess.value = '' }, 3000)
  } catch (err: any) {
    saveError.value = err.response?.data?.detail || 'Gagal menyimpan ke koleksi'
  } finally {
    savingToCollection.value = false
  }
}

async function createAndSave() {
  if (!newCollectionName.value.trim() || !paper.value) return
  savingToCollection.value = true
  saveError.value = ''
  try {
    const col = await collectionsStore.createCollection(newCollectionName.value)
    await api.post(`/collections/${col.id}/papers`, { paper_id: paper.value.id })
    saveSuccess.value = `Paper disimpan ke koleksi "${newCollectionName.value}"!`
    showSaveModal.value = false
    newCollectionName.value = ''
    setTimeout(() => { saveSuccess.value = '' }, 3000)
  } catch (err: any) {
    saveError.value = err.response?.data?.detail || 'Gagal membuat koleksi'
  } finally {
    savingToCollection.value = false
  }
}

// Safely parse summary response (handles nested JSON strings)
const summaryData = computed(() => {
  const raw = aiStore.summary as any
  if (!raw) return null

  let ringkasan = raw.ringkasan || raw.summary || ''
  let temuan = raw.temuan_utama || raw.key_findings || []
  let metodologi = raw.metodologi || raw.methodology || ''

  // If ringkasan looks like a JSON string, try to parse it
  if (typeof ringkasan === 'string' && ringkasan.trim().startsWith('{')) {
    try {
      const inner = JSON.parse(ringkasan)
      ringkasan = inner.ringkasan || inner.summary || ringkasan
      temuan = inner.temuan_utama || inner.key_findings || temuan
      metodologi = inner.metodologi || inner.methodology || metodologi
    } catch { /* keep as-is */ }
  }

  // Ensure temuan is an array
  if (typeof temuan === 'string') {
    try { temuan = JSON.parse(temuan) } catch { temuan = [] }
  }
  if (!Array.isArray(temuan)) temuan = []

  return { ringkasan, temuan, metodologi }
})

function formatAuthors(authors: string[]): string {
  if (!authors?.length) return 'Unknown authors'
  return authors.join(', ')
}

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/search')
  }
}

function parseMarkdown(text: string): string {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/__(.*?)__/g, '<strong>$1</strong>')
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>')
  html = html.replace(/`(.*?)`/g, '<code class="bg-zinc-100 px-1 rounded text-red-600 font-mono text-[11px]">$1</code>')
  
  const lines = html.split('\n')
  let inList = false
  const processedLines = lines.map(line => {
    const trimmed = line.trim()
    if (trimmed.startsWith('* ') || trimmed.startsWith('- ')) {
      const content = trimmed.substring(2)
      if (!inList) {
        inList = true
        return `<ul class="list-disc pl-4 space-y-1 my-1"><li>${content}</li>`
      }
      return `<li>${content}</li>`
    } else {
      if (inList) {
        inList = false
        return `</ul>\n${line}`
      }
      return line
    }
  })
  
  if (inList) {
    processedLines.push('</ul>')
  }
  
  html = processedLines.join('\n')
  html = html.replace(/\n/g, '<br>')
  return html
}
</script>

<template>
  <div class="px-6 py-5 w-full">
    <!-- Back button -->
    <button @click="goBack" class="mb-4 inline-flex items-center gap-1 text-sm text-[var(--color-text-sub)] hover:text-[var(--color-primary)] transition">
      <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M19 12H5m7-7l-7 7 7 7"/></svg>
      Kembali ke hasil pencarian
    </button>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center gap-2.5 py-16">
      <div class="h-6 w-6 animate-spin rounded-full border-2 border-[var(--color-primary)] border-t-transparent"></div>
      <span class="text-sm text-[var(--color-text-muted)]">Memuat detail paper...</span>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="rounded-lg border border-red-200 bg-red-50 p-5 text-center">
      <svg width="32" height="32" class="mx-auto text-red-400" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>
      <p class="mt-2 text-sm font-medium text-red-700">{{ error }}</p>
      <button @click="fetchPaper" class="mt-2 rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700 transition">Coba Lagi</button>
    </div>

    <!-- Success toast -->
    <div v-if="saveSuccess" class="fixed top-4 right-4 z-50 rounded-md bg-emerald-600 px-3.5 py-2 text-sm font-medium text-white shadow-lg">
      {{ saveSuccess }}
    </div>

    <!-- Paper Detail -->
    <div v-else-if="paper" class="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-5 items-start">
      <!-- Left: Paper Info -->
      <div>
        <!-- Header Card -->
        <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
          <div class="flex flex-wrap items-center gap-1.5 mb-2.5">
            <span class="rounded px-1.5 py-0.5 text-xs font-medium"
              :class="paper.source === 'arxiv' ? 'bg-violet-50 text-violet-600' : paper.source === 'uploaded' ? 'bg-emerald-50 text-emerald-600' : 'bg-blue-50 text-blue-600'">
              {{ paper.source === 'semantic_scholar' ? 'Semantic Scholar' : paper.source === 'arxiv' ? 'arXiv' : 'Uploaded' }}
            </span>
            <span v-if="paper.year" class="text-xs text-[var(--color-text-muted)]">{{ paper.year }}</span>
            <span v-for="field in (paper.fields_of_study || []).slice(0, 3)" :key="field"
              class="rounded bg-emerald-50 px-1.5 py-0.5 text-[10px] font-medium text-emerald-600">{{ field }}</span>
          </div>

          <h1 class="text-xl font-semibold leading-snug text-[var(--color-text)]">{{ paper.title }}</h1>
          <p class="mt-2 text-sm leading-relaxed text-[var(--color-text-sub)]">{{ formatAuthors(paper.authors) }}</p>

          <div class="mt-4 flex flex-wrap items-center gap-3 border-t border-[var(--color-border)] pt-3">
            <div v-if="paper.citation_count" class="flex items-center gap-1 text-sm text-[var(--color-text-sub)]">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M7 17l9.2-9.2M17 17V7H7"/></svg>
              <strong class="font-medium text-[var(--color-text)]">{{ paper.citation_count.toLocaleString() }}</strong> sitasi
            </div>
            <a v-if="paper.doi" :href="`https://doi.org/${paper.doi}`" target="_blank"
              class="flex items-center gap-1 text-sm text-[var(--color-primary)] hover:underline">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/></svg>
              DOI: {{ paper.doi }}
            </a>
            <span v-if="paper.page_count" class="text-sm text-[var(--color-text-muted)]">
              <svg width="14" height="14" class="inline mr-0.5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              {{ paper.page_count }} halaman
            </span>
          </div>

          <!-- Action Buttons -->
          <div class="mt-4 flex flex-wrap gap-2">
            <button @click="handleSummarize"
              class="flex items-center gap-1.5 rounded-md bg-[var(--color-primary)] px-3.5 py-2 text-sm font-medium text-white transition hover:bg-[var(--color-primary-hover)]">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M12 3v1m0 16v1m-8-9H3m18 0h-1"/><circle cx="12" cy="12" r="4"/></svg>
              AI Summarize
            </button>
            <button @click="showSaveModal = !showSaveModal"
              class="flex items-center gap-1.5 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-3.5 py-2 text-sm font-medium text-[var(--color-text-sub)] transition hover:bg-zinc-50">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M4 4.5A2.5 2.5 0 016.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15z"/></svg>
              Simpan ke Koleksi
            </button>
            <button @click="fetchRelated" :disabled="loadingRelated"
              class="flex items-center gap-1.5 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-3.5 py-2 text-sm font-medium text-[var(--color-text-sub)] transition hover:bg-zinc-50 disabled:opacity-50">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>
              {{ loadingRelated ? 'Mencari...' : 'Find Related' }}
            </button>
            <a v-if="paper.url" :href="paper.url" target="_blank"
              class="flex items-center gap-1.5 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-3.5 py-2 text-sm font-medium text-[var(--color-text-sub)] transition hover:bg-zinc-50">
              Buka Paper ↗
            </a>
          </div>

          <!-- Save to Collection Modal -->
          <div v-if="showSaveModal" class="mt-3.5 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] p-3.5">
            <h4 class="text-sm font-medium text-[var(--color-text)] mb-2.5">Pilih Koleksi:</h4>
            <div v-if="saveError" class="mb-2 rounded-md bg-red-50 px-2.5 py-1.5 text-xs text-red-600">{{ saveError }}</div>
            <!-- Existing collections -->
            <div v-if="collectionsStore.collections.length" class="flex flex-col gap-1 mb-2.5">
              <button v-for="col in collectionsStore.collections" :key="col.id"
                @click="saveToCollection(col.id)" :disabled="savingToCollection"
                class="flex items-center justify-between rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-2.5 py-1.5 text-left text-xs transition hover:border-zinc-300 disabled:opacity-50">
                <span class="font-medium text-[var(--color-text)]">{{ col.name }}</span>
                <span class="text-[var(--color-text-muted)]">Simpan →</span>
              </button>
            </div>
            <div v-else class="mb-2.5 text-xs text-[var(--color-text-muted)]">Belum ada koleksi.</div>
            <!-- Create new -->
            <div class="border-t border-[var(--color-border)] pt-2.5">
              <label class="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider">Buat Koleksi Baru</label>
              <div class="mt-1 flex gap-1.5">
                <input v-model="newCollectionName" type="text" placeholder="Nama koleksi..."
                  class="flex-1 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-2.5 py-1.5 text-xs outline-none focus:border-[var(--color-primary)]"
                  @keyup.enter="createAndSave" />
                <button @click="createAndSave" :disabled="!newCollectionName.trim() || savingToCollection"
                  class="rounded-md bg-[var(--color-primary)] px-2.5 py-1.5 text-xs font-medium text-white disabled:opacity-50 transition hover:bg-[var(--color-primary-hover)]">
                  {{ savingToCollection ? '...' : 'Buat & Simpan' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Abstract -->
        <div v-if="paper.abstract" class="mt-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
          <div class="flex items-center justify-between mb-2.5">
            <h2 class="text-sm font-medium text-[var(--color-text)]">Abstrak</h2>
            <button @click="translateAbstract" :disabled="translatingAbstract || !!translatedAbstract"
              class="flex items-center gap-1 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-2.5 py-1 text-xs font-medium text-[var(--color-text-sub)] transition hover:bg-zinc-50 disabled:opacity-50">
              <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>
              {{ translatingAbstract ? 'Menerjemahkan...' : translatedAbstract ? 'Sudah diterjemahkan' : 'Terjemahkan ke Indonesia' }}
            </button>
          </div>
          <p class="text-sm leading-[1.75] text-[var(--color-text-sub)] whitespace-pre-line">{{ paper.abstract }}</p>

          <!-- Translated Abstract -->
          <div v-if="translatedAbstract" class="mt-3 rounded-md bg-blue-50 border border-blue-200 p-3.5">
            <div class="flex items-center gap-1.5 mb-1.5">
              <span class="text-[10px] font-medium uppercase tracking-wider text-blue-600">Terjemahan (AI)</span>
            </div>
            <p class="text-sm leading-[1.7] text-[var(--color-text)] whitespace-pre-line">{{ translatedAbstract }}</p>
          </div>
        </div>

        <!-- Related Papers -->
        <div v-if="loadingRelated" class="mt-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-5 text-center">
          <div class="flex flex-col items-center gap-2.5 py-3">
            <div class="h-5 w-5 animate-spin rounded-full border-2 border-[var(--color-primary)] border-t-transparent"></div>
            <span class="text-sm text-[var(--color-text-muted)]">Mencari paper terkait dengan AI...</span>
          </div>
        </div>
        <div v-else-if="relatedPapers.length" class="mt-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
          <h2 class="text-sm font-medium text-[var(--color-text)] mb-3">Paper Terkait ({{ relatedPapers.length }})</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <div v-for="rp in relatedPapers" :key="rp.id || rp.external_id"
              @click="router.push(`/papers/${rp.id}`)"
              class="cursor-pointer rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] p-3 transition hover:border-zinc-300">
              <div class="text-sm font-medium leading-snug text-[var(--color-text)] line-clamp-2">{{ rp.title }}</div>
              <div class="mt-1 text-xs text-[var(--color-text-muted)]">
                {{ (rp.authors || []).slice(0, 2).join(', ') }} {{ rp.year ? `· ${rp.year}` : '' }}
              </div>
              <div v-if="rp.citation_count" class="mt-0.5 text-xs text-[var(--color-text-muted)]">
                <svg width="10" height="10" class="inline mr-0.5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M7 17l9.2-9.2M17 17V7H7"/></svg>
                {{ rp.citation_count.toLocaleString() }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: AI Panel (sticky) -->
      <div class="lg:sticky lg:top-5">
        <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] overflow-hidden">
          <!-- Tips Akurasi Abstrak -->
          <div v-if="paper.source !== 'uploaded'" class="bg-amber-50 border-b border-amber-100 p-3 text-[11px] text-amber-900 leading-relaxed flex items-start gap-2">
            <svg width="14" height="14" class="flex-shrink-0 text-amber-600 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>
            <div>
              <strong>💡 Tips Akurasi:</strong> Paper ini bersumber dari pencarian luar sehingga AI hanya membaca <strong>Abstrak</strong> saja. Unduh PDF asli paper ini lalu unggah lewat menu <strong>Upload PDF</strong> untuk analisis & tanya-jawab yang 100% akurat.
            </div>
          </div>

          <!-- Card Header & Tabs -->
          <div class="bg-[var(--color-bg)] border-b border-[var(--color-border)] p-1 flex gap-0.5">
            <button @click="activeAiTab = 'summary'"
              class="flex-1 rounded px-2.5 py-1.5 text-xs font-medium transition"
              :class="activeAiTab === 'summary' ? 'bg-[var(--color-surface)] text-[var(--color-text)] shadow-sm border border-zinc-200' : 'text-[var(--color-text-sub)] hover:text-[var(--color-text)]'">
              Ringkasan
            </button>
            <button @click="activeAiTab = 'chat'"
              class="flex-1 rounded px-2.5 py-1.5 text-xs font-medium transition"
              :class="activeAiTab === 'chat' ? 'bg-[var(--color-surface)] text-[var(--color-text)] shadow-sm border border-zinc-200' : 'text-[var(--color-text-sub)] hover:text-[var(--color-text)]'">
              Tanya AI
            </button>
            <button @click="activeAiTab = 'explain'"
              class="flex-1 rounded px-2.5 py-1.5 text-xs font-medium transition"
              :class="activeAiTab === 'explain' ? 'bg-[var(--color-surface)] text-[var(--color-text)] shadow-sm border border-zinc-200' : 'text-[var(--color-text-sub)] hover:text-[var(--color-text)]'">
              Jelaskan
            </button>
          </div>

          <div class="p-4">
            <!-- TAB: SUMMARY -->
            <div v-if="activeAiTab === 'summary'">
              <div v-if="!aiStore.summary && !aiStore.loading" class="py-4 text-center">
                <svg width="32" height="32" class="mx-auto text-[var(--color-primary)]" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M12 3v1m0 16v1m-8-9H3m18 0h-1"/><circle cx="12" cy="12" r="4"/></svg>
                <h3 class="mt-2 text-sm font-medium text-[var(--color-text)]">AI Paper Summarizer</h3>
                <p class="mt-1 text-xs text-[var(--color-text-sub)] leading-relaxed">
                  Dapatkan ringkasan paper ini dalam bahasa Indonesia yang mudah dipahami.
                </p>
                <button @click="handleSummarize"
                  class="mt-3 w-full rounded-md bg-[var(--color-primary)] py-2 text-xs font-medium text-white transition hover:bg-[var(--color-primary-hover)]">
                  Generate Summary
                </button>
              </div>

              <div v-else>
                <!-- Loading -->
                <div v-if="aiStore.loading" class="flex flex-col items-center gap-2.5 py-6">
                  <div class="h-5 w-5 animate-spin rounded-full border-2 border-[var(--color-primary)] border-t-transparent"></div>
                  <span class="text-xs text-[var(--color-text-muted)]">Generating summary...</span>
                </div>

                <!-- Result -->
                <div v-else-if="summaryData">
                  <div class="mb-3.5">
                    <div class="text-[10px] font-medium uppercase tracking-wider text-[var(--color-text-muted)] mb-1">Ringkasan</div>
                    <p class="text-xs leading-[1.65] text-[var(--color-text-sub)] whitespace-pre-wrap">{{ summaryData.ringkasan || 'Ringkasan tidak tersedia.' }}</p>
                  </div>

                  <div v-if="summaryData.temuan.length" class="mb-3.5">
                    <div class="text-[10px] font-medium uppercase tracking-wider text-[var(--color-text-muted)] mb-1.5">Temuan Utama</div>
                    <div v-for="(f, i) in summaryData.temuan" :key="i" class="flex gap-1.5 items-start mb-1">
                      <svg width="12" height="12" class="mt-0.5 flex-shrink-0 text-emerald-500" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
                      <span class="text-xs text-[var(--color-text-sub)] leading-normal">{{ f }}</span>
                    </div>
                  </div>

                  <div v-if="summaryData.metodologi" class="rounded-md bg-amber-50 border border-amber-100 p-2.5">
                    <div class="text-[10px] font-medium uppercase tracking-wider text-amber-600 mb-1">Metodologi</div>
                    <p class="text-xs leading-[1.5] text-amber-900">{{ summaryData.metodologi }}</p>
                  </div>

                  <button @click="handleSummarize"
                    class="mt-3.5 w-full rounded-md border border-[var(--color-border)] py-1.5 text-xs font-medium text-[var(--color-text-sub)] hover:bg-zinc-50 transition">
                    Regenerate Summary
                  </button>
                </div>
              </div>
            </div>

            <!-- TAB: CHAT -->
            <div v-if="activeAiTab === 'chat'" class="flex flex-col h-[380px] justify-between">
              <!-- Chat Messages -->
              <div class="flex-1 overflow-y-auto mb-3 pr-1 space-y-2.5">
                <div class="rounded-md bg-zinc-50 border border-zinc-100 p-2.5 text-xs text-[var(--color-text-sub)] leading-relaxed">
                  Halo! Tanyakan apa saja mengenai paper ini (metodologi, hasil, batasan, dll.). Saya akan menjawab berdasarkan konten paper.
                </div>
                
                <div v-for="(msg, idx) in chatMessages" :key="idx"
                  class="flex flex-col max-w-[85%]"
                  :class="msg.role === 'user' ? 'ml-auto items-end' : 'mr-auto items-start'">
                  <div class="rounded-lg p-2.5 text-xs leading-relaxed"
                    :class="msg.role === 'user' ? 'bg-[var(--color-primary)] text-white' : 'bg-zinc-100 text-[var(--color-text)] border border-zinc-200'"
                    v-html="parseMarkdown(msg.content)">
                  </div>
                </div>

                <div v-if="chatLoading" class="flex items-center gap-1.5 text-xs text-[var(--color-text-muted)] p-1">
                  <div class="h-3 w-3 animate-spin rounded-full border border-[var(--color-primary)] border-t-transparent"></div>
                  <span>AI sedang mengetik...</span>
                </div>

                <div v-if="chatError" class="rounded-md bg-red-50 border border-red-100 p-2 text-xs text-red-600">
                  {{ chatError }}
                </div>
              </div>

              <!-- Input Area -->
              <div class="border-t border-[var(--color-border)] pt-2.5 flex gap-1.5">
                <input v-model="chatQuery" type="text" placeholder="Tanya sesuatu tentang paper..."
                  class="flex-1 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-2.5 py-1.5 text-xs outline-none focus:border-[var(--color-primary)]"
                  @keyup.enter="sendChatMessage" :disabled="chatLoading" />
                <button @click="sendChatMessage" :disabled="!chatQuery.trim() || chatLoading"
                  class="rounded-md bg-[var(--color-primary)] px-2.5 py-1.5 text-xs font-medium text-white transition hover:bg-[var(--color-primary-hover)] disabled:opacity-50">
                  Kirim
                </button>
              </div>
            </div>

            <!-- TAB: EXPLAIN -->
            <div v-if="activeAiTab === 'explain'">
              <h3 class="text-xs font-medium text-[var(--color-text)] mb-2.5 flex items-center gap-1.5">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
                Jelaskan Istilah/Teks
              </h3>
              <textarea v-model="explainText"
                placeholder="Paste bagian paper yang ingin dijelaskan secara sederhana..."
                rows="4"
                class="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-xs outline-none resize-none transition focus:border-[var(--color-primary)]"
              ></textarea>
              <div class="mt-2 flex gap-1.5">
                <button @click="handleExplain" :disabled="!explainText.trim() || explainLoading"
                  class="rounded-md bg-[var(--color-primary)] px-3 py-1.5 text-xs font-medium text-white transition hover:bg-[var(--color-primary-hover)] disabled:opacity-50">
                  {{ explainLoading ? 'Menjelaskan...' : 'Jelaskan (ID)' }}
                </button>
              </div>
              
              <!-- Explain Result -->
              <div v-if="explainResult" class="mt-3 rounded-md bg-blue-50 border border-blue-100 p-3">
                <div class="text-[10px] font-medium uppercase tracking-wider text-blue-600 mb-1">Penjelasan AI</div>
                <p class="text-xs leading-[1.65] text-blue-900 whitespace-pre-wrap">{{ explainResult }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
