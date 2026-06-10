<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUploadStore } from '@/stores/upload'
import { useCollectionsStore, type CollectionPaper } from '@/stores/collections'
import { useAIStore } from '@/stores/ai'
import api from '@/services/api'

const uploadStore = useUploadStore()
const collectionsStore = useCollectionsStore()
const aiStore = useAIStore()

const activeTab = ref<'upload' | 'select' | 'result'>('select')
const selectedIds = ref<Set<string>>(new Set())
const dragOver = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

// Source filter: 'all' | 'uploaded' | collection_id
const sourceFilter = ref('all')
const collectionPapers = ref<CollectionPaper[]>([])
const loadingCollection = ref(false)
const selectedCollectionId = ref<string | null>(null)

onMounted(async () => {
  await Promise.all([
    uploadStore.fetchPapers(),
    collectionsStore.fetchCollections(),
  ])
})

// All available papers merged from uploads + collections
const allPapers = computed(() => {
  const papers: Array<{
    id: string
    title: string
    authors: string[]
    year: number | null
    page_count: number | null
    source: string
    source_label: string
  }> = []

  // Add uploaded papers
  if (sourceFilter.value === 'all' || sourceFilter.value === 'uploaded') {
    for (const p of uploadStore.papers) {
      papers.push({
        id: p.id,
        title: p.title,
        authors: p.authors || [],
        year: p.year,
        page_count: p.page_count,
        source: 'uploaded',
        source_label: 'Uploaded',
      })
    }
  }

  // Add collection papers
  if (sourceFilter.value === 'all') {
    for (const p of collectionPapers.value) {
      // Avoid duplicates (same paper in upload + collection)
      if (!papers.find((existing) => existing.id === p.id)) {
        papers.push({
          id: p.id,
          title: p.title,
          authors: p.authors || [],
          year: p.year,
          page_count: p.page_count,
          source: 'collection',
          source_label: getCollectionName(selectedCollectionId.value || ''),
        })
      }
    }
  } else if (sourceFilter.value !== 'uploaded' && sourceFilter.value !== 'all') {
    // Specific collection selected
    for (const p of collectionPapers.value) {
      if (!papers.find((existing) => existing.id === p.id)) {
        papers.push({
          id: p.id,
          title: p.title,
          authors: p.authors || [],
          year: p.year,
          page_count: p.page_count,
          source: 'collection',
          source_label: getCollectionName(sourceFilter.value),
        })
      }
    }
  }

  return papers
})

function getCollectionName(id: string): string {
  const col = collectionsStore.collections.find((c) => c.id === id)
  return col?.name || 'Collection'
}

async function onSourceFilterChange(newFilter: string) {
  sourceFilter.value = newFilter
  collectionPapers.value = []
  selectedCollectionId.value = null

  if (newFilter !== 'all' && newFilter !== 'uploaded') {
    await loadCollectionPapers(newFilter)
  } else if (newFilter === 'all') {
    // Load all collection papers
    await loadAllCollectionPapers()
  }
}

async function loadCollectionPapers(collectionId: string) {
  loadingCollection.value = true
  selectedCollectionId.value = collectionId
  try {
    const detail = await collectionsStore.fetchCollectionDetail(collectionId)
    if (detail) {
      collectionPapers.value = detail.papers
    }
  } catch {
    collectionPapers.value = []
  } finally {
    loadingCollection.value = false
  }
}

async function loadAllCollectionPapers() {
  loadingCollection.value = true
  try {
    const all: CollectionPaper[] = []
    for (const col of collectionsStore.collections) {
      const detail = await collectionsStore.fetchCollectionDetail(col.id)
      if (detail) {
        for (const p of detail.papers) {
          if (!all.find((existing) => existing.id === p.id)) {
            all.push(p)
          }
        }
      }
    }
    collectionPapers.value = all
  } catch {
    collectionPapers.value = []
  } finally {
    loadingCollection.value = false
  }
}

const selectedCount = computed(() => selectedIds.value.size)
const canAnalyze = computed(() => selectedCount.value >= 3 && selectedCount.value <= 10)

function togglePaper(id: string) {
  const s = new Set(selectedIds.value)
  if (s.has(id)) s.delete(id)
  else if (s.size < 10) s.add(id)
  selectedIds.value = s
}

function isSelected(id: string) {
  return selectedIds.value.has(id)
}

function selectAll() {
  const s = new Set(selectedIds.value)
  for (const p of allPapers.value) {
    if (s.size >= 10) break
    s.add(p.id)
  }
  selectedIds.value = s
}

function deselectAll() {
  selectedIds.value = new Set()
}

async function handleFileUpload(file: File) {
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    uploadStore.uploadError = 'Hanya file PDF yang diterima'
    return
  }
  await uploadStore.uploadPaper(file)
  if (!uploadStore.uploadError) {
    const latest = uploadStore.papers[0]
    if (latest) {
      const s = new Set(selectedIds.value)
      s.add(latest.id)
      selectedIds.value = s
    }
  }
}

function onDrop(e: DragEvent) {
  dragOver.value = false
  const files = e.dataTransfer?.files
  if (files) {
    for (const file of Array.from(files)) {
      handleFileUpload(file)
    }
  }
}

function onFileSelect(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files) {
    for (const file of Array.from(target.files)) {
      handleFileUpload(file)
    }
  }
  target.value = ''
}

async function runAnalysis() {
  activeTab.value = 'result'
  await aiStore.analyzeGaps(Array.from(selectedIds.value))
}

function resetAnalysis() {
  activeTab.value = 'select'
  aiStore.gapResult = null
}

const gapData = computed(() => {
  const g = aiStore.gapResult as any
  if (!g) return null
  return {
    topik: g.topik_dominan || [],
    metodologi: g.metodologi || [],
    celah: g.celah_penelitian || [],
    saran: g.saran_topik || [],
    raw: g.raw_response || null,
  }
})

function formatAuthors(authors: string[]): string {
  if (!authors?.length) return 'Unknown'
  if (authors.length <= 3) return authors.join(', ')
  return `${authors.slice(0, 3).join(', ')} et al.`
}

const activeGapIndex = ref<number | null>(null)

function selectGap(index: number) {
  activeGapIndex.value = index
  setTimeout(() => {
    const el = document.getElementById(`gap-card-${index}`)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, 100)
}

const gapMatrix = computed(() => {
  if (!gapData.value) return null

  const frequentMethods = gapData.value.metodologi
    .filter((m: any) => m.freq === 'Sering')
    .map((m: any) => m.name.toLowerCase())

  const q1: any[] = [] // High Priority, Low Frequency (Goldmine)
  const q2: any[] = [] // High Priority, High Frequency (Kompetitif)
  const q3: any[] = [] // Medium Priority, Low Frequency (Niche)
  const q4: any[] = [] // Medium Priority, High Frequency (Kolektif)

  gapData.value.celah.forEach((g: any, index: number) => {
    const text = (g.title + ' ' + g.desc).toLowerCase()
    const isFrequent = frequentMethods.some((method: string) => text.includes(method))
    const item = { ...g, originalIndex: index }

    if (g.priority === 'Tinggi') {
      if (isFrequent) {
        q2.push(item)
      } else {
        q1.push(item)
      }
    } else {
      if (isFrequent) {
        q4.push(item)
      } else {
        q3.push(item)
      }
    }
  })

  return { q1, q2, q3, q4 }
})

// Gap Chat state
const gapChatQuery = ref('')
const gapChatMessages = ref<{ role: 'user' | 'assistant', content: string }[]>([])
const gapChatLoading = ref(false)
const gapChatError = ref('')

async function sendGapChatMessage() {
  if (!gapChatQuery.value.trim() || gapChatLoading.value || !selectedIds.value.size) return
  
  const userText = gapChatQuery.value.trim()
  gapChatQuery.value = ''
  gapChatError.value = ''
  
  gapChatMessages.value.push({ role: 'user', content: userText })
  gapChatLoading.value = true
  
  try {
    const { data } = await api.post('/ai/gap-chat', {
      paper_ids: Array.from(selectedIds.value),
      messages: gapChatMessages.value
    })
    gapChatMessages.value.push({ role: 'assistant', content: data.reply })
  } catch (err: any) {
    gapChatError.value = err.response?.data?.detail || 'Gagal mengirim pesan ke AI'
  } finally {
    gapChatLoading.value = false
  }
}

function selectQuickPrompt(text: string) {
  gapChatQuery.value = text
  sendGapChatMessage()
}

function clearGapChat() {
  gapChatMessages.value = []
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
    <div class="mb-5 flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-[var(--color-text)]">Research Gap Analysis</h1>
        <p class="mt-0.5 text-sm text-[var(--color-text-sub)]">Pilih minimal 3 paper dari upload atau koleksi, lalu analisis celah penelitiannya</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="mb-5 flex gap-0.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-0.5">
      <button @click="activeTab = 'upload'"
        class="flex-1 rounded-md py-2 text-sm font-medium transition"
        :class="activeTab === 'upload' ? 'bg-[var(--color-surface)] text-[var(--color-text)] shadow-sm' : 'text-[var(--color-text-sub)] hover:text-[var(--color-text)]'">
        Upload PDF
      </button>
      <button @click="activeTab = 'select'"
        class="flex-1 rounded-md py-2 text-sm font-medium transition"
        :class="activeTab === 'select' ? 'bg-[var(--color-surface)] text-[var(--color-text)] shadow-sm' : 'text-[var(--color-text-sub)] hover:text-[var(--color-text)]'">
        Pilih Paper ({{ selectedCount }}/10)
      </button>
      <button @click="activeTab = 'result'" :disabled="!aiStore.gapResult"
        class="flex-1 rounded-md py-2 text-sm font-medium transition disabled:opacity-40"
        :class="activeTab === 'result' ? 'bg-[var(--color-surface)] text-[var(--color-text)] shadow-sm' : 'text-[var(--color-text-sub)] hover:text-[var(--color-text)]'">
        Hasil Analisis
      </button>
    </div>

    <!-- Tab: Upload -->
    <div v-if="activeTab === 'upload'">
      <div
        @dragover.prevent="dragOver = true"
        @dragleave="dragOver = false"
        @drop.prevent="onDrop"
        @click="fileInput?.click()"
        class="cursor-pointer rounded-lg border-2 border-dashed p-10 text-center transition"
        :class="dragOver ? 'border-[var(--color-primary)] bg-[var(--color-primary-soft)]' : 'border-[var(--color-border)] bg-[var(--color-surface)] hover:border-zinc-300'">
        <input ref="fileInput" type="file" accept=".pdf" multiple class="hidden" @change="onFileSelect" />
        <svg width="40" height="40" class="mx-auto text-[var(--color-text-muted)]" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
        <h3 class="mt-2 text-sm font-medium text-[var(--color-text)]">
          {{ uploadStore.uploading ? 'Memproses PDF...' : 'Drag & drop PDF di sini' }}
        </h3>
        <p class="mt-1 text-sm text-[var(--color-text-sub)]">atau klik untuk memilih file (max 50 MB)</p>
        <div v-if="uploadStore.uploading" class="mt-3 flex justify-center">
          <div class="h-6 w-6 animate-spin rounded-full border-2 border-[var(--color-primary)] border-t-transparent"></div>
        </div>
      </div>

      <div v-if="uploadStore.uploadError" class="mt-2.5 rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
        {{ uploadStore.uploadError }}
      </div>

      <div v-if="uploadStore.papers.length" class="mt-5">
        <h3 class="mb-2.5 text-sm font-medium text-[var(--color-text)]">Uploaded Papers ({{ uploadStore.papers.length }})</h3>
        <div class="flex flex-col gap-2">
          <div v-for="paper in uploadStore.papers" :key="paper.id"
            class="flex items-center justify-between rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-3.5 py-2.5">
            <div class="min-w-0 flex-1">
              <div class="text-sm font-medium text-[var(--color-text)] truncate">{{ paper.title }}</div>
              <div class="text-xs text-[var(--color-text-sub)] mt-0.5">
                {{ paper.authors?.join(', ') || 'Unknown' }}
                <span v-if="paper.year"> · {{ paper.year }}</span>
              </div>
            </div>
            <div class="flex items-center gap-1.5 ml-3 flex-shrink-0">
              <span v-if="isSelected(paper.id)" class="text-xs font-medium text-[var(--color-primary)] bg-[var(--color-primary-soft)] px-1.5 py-0.5 rounded">Terpilih</span>
              <button @click="uploadStore.deletePaper(paper.id)"
                class="rounded-md border border-[var(--color-border)] px-2 py-1 text-xs text-red-500 hover:bg-red-50 transition">Hapus</button>
            </div>
          </div>
        </div>
      </div>

      <button @click="activeTab = 'select'"
        class="mt-3.5 w-full rounded-md bg-[var(--color-primary)] py-2.5 text-sm font-medium text-white transition hover:bg-[var(--color-primary-hover)]">
        Lanjut pilih paper →
      </button>
    </div>

    <!-- Tab: Select Papers -->
    <div v-if="activeTab === 'select'">
      <!-- Warning Banner -->
      <div class="mb-4 rounded-md bg-amber-50 border border-amber-200 p-3 text-xs text-amber-900 leading-relaxed flex items-start gap-2.5">
        <svg width="16" height="16" class="flex-shrink-0 text-amber-600 mt-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>
        <div>
          <strong>💡 Tips Akurasi:</strong> Analisis celah riset akan <strong>jauh lebih akurat</strong> jika Anda menggunakan paper hasil <strong>Upload PDF</strong>. Paper hasil pencarian eksternal hanya memiliki data <strong>Abstrak</strong> saja di database, sehingga hasil analisis AI akan bersifat lebih umum. Anda disarankan mengunduh PDF asli paper yang Anda pilih dan mengunggahnya terlebih dahulu.
        </div>
      </div>

      <!-- Source Filter -->
      <div class="mb-3.5 flex flex-wrap items-center gap-1.5">
        <span class="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider">Sumber:</span>
        <button @click="onSourceFilterChange('all')"
          class="rounded-md px-3 py-1 text-xs font-medium transition"
          :class="sourceFilter === 'all' ? 'bg-[var(--color-primary-soft)] text-[var(--color-primary)]' : 'bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-sub)] hover:bg-zinc-50'">
          Semua
        </button>
        <button @click="onSourceFilterChange('uploaded')"
          class="rounded-md px-3 py-1 text-xs font-medium transition"
          :class="sourceFilter === 'uploaded' ? 'bg-emerald-50 text-emerald-600' : 'bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-sub)] hover:bg-zinc-50'">
          Uploaded ({{ uploadStore.papers.length }})
        </button>
        <button v-for="col in collectionsStore.collections" :key="col.id"
          @click="onSourceFilterChange(col.id)"
          class="rounded-md px-3 py-1 text-xs font-medium transition"
          :class="sourceFilter === col.id ? 'bg-violet-50 text-violet-600' : 'bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-sub)] hover:bg-zinc-50'">
          {{ col.name }} ({{ col.paper_count || 0 }})
        </button>
      </div>

      <!-- Counter + actions -->
      <div class="mb-3.5 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="rounded-md px-2.5 py-1 text-sm font-medium"
            :class="canAnalyze ? 'bg-[var(--color-primary-soft)] text-[var(--color-primary)]' : 'bg-zinc-100 text-[var(--color-text-muted)]'">
            {{ selectedCount }} / 10 dipilih
          </div>
          <span class="text-xs text-[var(--color-text-sub)]">Minimal 3 paper</span>
        </div>
        <div class="flex gap-1.5">
          <button @click="selectAll" class="rounded-md border border-[var(--color-border)] px-2.5 py-1 text-xs text-[var(--color-text-sub)] hover:bg-zinc-50 transition">Pilih Semua</button>
          <button @click="deselectAll" class="rounded-md border border-[var(--color-border)] px-2.5 py-1 text-xs text-[var(--color-text-sub)] hover:bg-zinc-50 transition">Reset</button>
        </div>
      </div>

      <!-- Progress bar -->
      <div class="mb-3.5 h-1 w-full rounded-full bg-zinc-100">
        <div class="h-full rounded-full transition-all duration-300"
          :style="{ width: `${(selectedCount / 10) * 100}%` }"
          :class="canAnalyze ? 'bg-[var(--color-primary)]' : 'bg-zinc-300'"></div>
      </div>

      <!-- Loading -->
      <div v-if="loadingCollection" class="flex justify-center py-6">
        <div class="h-5 w-5 animate-spin rounded-full border-2 border-[var(--color-primary)] border-t-transparent"></div>
      </div>

      <!-- Paper Grid -->
      <div v-else-if="allPapers.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4">
        <div v-for="paper in allPapers" :key="paper.id"
          @click="togglePaper(paper.id)"
          class="cursor-pointer rounded-lg border p-3.5 transition"
          :class="isSelected(paper.id) ? 'border-[var(--color-primary)] bg-[var(--color-primary-soft)] ring-1 ring-[var(--color-primary)]/20' : 'border-[var(--color-border)] bg-[var(--color-surface)] hover:border-zinc-300'">
          <div class="flex items-start gap-2.5">
            <div class="mt-0.5 flex h-4 w-4 flex-shrink-0 items-center justify-center rounded border transition"
              :class="isSelected(paper.id) ? 'border-[var(--color-primary)] bg-[var(--color-primary)]' : 'border-zinc-300'">
              <svg v-if="isSelected(paper.id)" width="10" height="10" fill="none" stroke="white" stroke-width="2.5" viewBox="0 0 24 24">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1.5 mb-0.5">
                <span class="rounded px-1.5 py-0.5 text-[9px] font-medium"
                  :class="paper.source === 'uploaded' ? 'bg-emerald-50 text-emerald-600' : 'bg-violet-50 text-violet-600'">
                  {{ paper.source_label }}
                </span>
              </div>
              <div class="text-sm font-medium text-[var(--color-text)] leading-snug line-clamp-2">{{ paper.title }}</div>
              <div class="text-xs text-[var(--color-text-sub)] mt-1">
                {{ formatAuthors(paper.authors) }}
              </div>
              <div class="flex gap-2.5 mt-1.5 text-xs text-[var(--color-text-muted)]">
                <span v-if="paper.year">{{ paper.year }}</span>
                <span v-if="paper.page_count">{{ paper.page_count }} hal</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty -->
      <div v-else class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] py-10 text-center">
        <svg width="36" height="36" class="mx-auto text-[var(--color-text-muted)]" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        <p class="mt-2 text-sm text-[var(--color-text-sub)]">
          Belum ada paper. Upload PDF atau simpan paper dari pencarian ke koleksi terlebih dahulu.
        </p>
        <div class="mt-3 flex justify-center gap-2">
          <button @click="activeTab = 'upload'" class="rounded-md bg-[var(--color-primary)] px-3.5 py-1.5 text-sm font-medium text-white">Upload PDF</button>
          <router-link to="/search" class="rounded-md border border-[var(--color-border)] px-3.5 py-1.5 text-sm font-medium text-[var(--color-text-sub)] hover:bg-zinc-50 transition">Cari Paper</router-link>
        </div>
      </div>

      <!-- Analyze Button -->
      <button @click="runAnalysis" :disabled="!canAnalyze"
        class="mt-5 flex w-full items-center justify-center gap-2 rounded-md py-2.5 text-sm font-medium transition"
        :class="canAnalyze ? 'bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)]' : 'bg-zinc-100 text-zinc-400 cursor-not-allowed'">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        Analisis Research Gap ({{ selectedCount }} paper)
      </button>
    </div>

    <!-- Tab: Results -->
    <div v-if="activeTab === 'result'">
      <!-- Loading -->
      <div v-if="aiStore.loading" class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] py-16 text-center">
        <div class="flex justify-center mb-3">
          <div class="h-8 w-8 animate-spin rounded-full border-2 border-[var(--color-primary)] border-t-transparent"></div>
        </div>
        <h3 class="text-sm font-medium text-[var(--color-text)]">AI sedang menganalisis...</h3>
        <p class="mt-1 text-sm text-[var(--color-text-sub)]">Membaca {{ selectedCount }} paper dan mengidentifikasi celah penelitian</p>
      </div>

      <div v-else-if="gapData">
        <div class="mb-4 rounded-lg bg-[var(--color-bg)] border border-[var(--color-border)] px-4 py-3 flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <svg width="16" height="16" class="text-[var(--color-primary)]" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
              <path d="M12 3v1m0 16v1m-8-9H3m18 0h-1m-2.636-6.364l-.707.707M6.343 17.657l-.707.707m0-12.728l.707.707m11.314 11.314l.707.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
            </svg>
            <div>
              <div class="text-sm font-medium text-[var(--color-text)]">Analisis Selesai</div>
              <div class="text-xs text-[var(--color-text-sub)]">Berdasarkan {{ selectedCount }} paper · Powered by Groq AI</div>
            </div>
          </div>
          <button @click="resetAnalysis" class="rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-2.5 py-1 text-xs font-medium text-[var(--color-text-sub)] hover:bg-zinc-50 transition">Analisis Ulang</button>
        </div>

        <!-- Matriks Prioritas & Frekuensi Celah Riset -->
        <div v-if="gapMatrix" class="mb-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-sm font-medium text-[var(--color-text)] flex items-center gap-1.5">
              <svg width="14" height="14" class="text-[var(--color-primary)]" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z"/></svg>
              Matriks Prioritas & Frekuensi Celah Riset
            </h2>
            <span class="text-[10px] text-[var(--color-text-muted)] font-medium">Klik badge celah untuk melihat detail</span>
          </div>

          <div class="grid grid-cols-[30px_1fr] gap-2">
            <!-- Y-Axis Label (Vertical text) -->
            <div class="flex flex-col justify-around items-center text-[10px] font-bold text-[var(--color-text-muted)] uppercase tracking-wider [writing-mode:vertical-lr] rotate-180 py-4 border-r border-[var(--color-border)]">
              <span>Prioritas Tinggi</span>
              <span class="my-auto text-zinc-300">|</span>
              <span>Prioritas Sedang</span>
            </div>

            <div>
              <!-- Matrix Grid (2x2) -->
              <div class="grid grid-cols-2 gap-2 border border-[var(--color-border)] rounded-lg overflow-hidden bg-zinc-50/50 p-2">
                <!-- Q1: Goldmine (Tinggi, Jarang) -->
                <div class="bg-white rounded-md border border-zinc-100 p-3 flex flex-col min-h-[110px]">
                  <div class="text-[10px] font-bold text-emerald-600 uppercase tracking-wider mb-2 flex items-center gap-1">
                    <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                    1. Goldmine (Peluang Utama)
                  </div>
                  <div class="flex flex-wrap gap-1.5 overflow-y-auto">
                    <button v-for="g in gapMatrix.q1" :key="g.originalIndex"
                      @click="selectGap(g.originalIndex)"
                      class="rounded bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 px-2 py-1 text-[10px] font-medium text-emerald-700 text-left transition truncate max-w-full">
                      {{ g.title }}
                    </button>
                    <span v-if="!gapMatrix.q1.length" class="text-[10px] text-[var(--color-text-muted)] italic">Tidak ada celah</span>
                  </div>
                </div>

                <!-- Q2: Kompetitif (Tinggi, Sering) -->
                <div class="bg-white rounded-md border border-zinc-100 p-3 flex flex-col min-h-[110px]">
                  <div class="text-[10px] font-bold text-rose-600 uppercase tracking-wider mb-2 flex items-center gap-1">
                    <span class="h-1.5 w-1.5 rounded-full bg-rose-500"></span>
                    2. Kompetitif (Mainstream)
                  </div>
                  <div class="flex flex-wrap gap-1.5 overflow-y-auto">
                    <button v-for="g in gapMatrix.q2" :key="g.originalIndex"
                      @click="selectGap(g.originalIndex)"
                      class="rounded bg-rose-50 hover:bg-rose-100 border border-rose-200 px-2 py-1 text-[10px] font-medium text-rose-700 text-left transition truncate max-w-full">
                      {{ g.title }}
                    </button>
                    <span v-if="!gapMatrix.q2.length" class="text-[10px] text-[var(--color-text-muted)] italic">Tidak ada celah</span>
                  </div>
                </div>

                <!-- Q3: Niche (Sedang, Jarang) -->
                <div class="bg-white rounded-md border border-zinc-100 p-3 flex flex-col min-h-[110px]">
                  <div class="text-[10px] font-bold text-blue-600 uppercase tracking-wider mb-2 flex items-center gap-1">
                    <span class="h-1.5 w-1.5 rounded-full bg-blue-500"></span>
                    3. Niche (Eksploratif)
                  </div>
                  <div class="flex flex-wrap gap-1.5 overflow-y-auto">
                    <button v-for="g in gapMatrix.q3" :key="g.originalIndex"
                      @click="selectGap(g.originalIndex)"
                      class="rounded bg-blue-50 hover:bg-blue-100 border border-blue-200 px-2 py-1 text-[10px] font-medium text-blue-700 text-left transition truncate max-w-full">
                      {{ g.title }}
                    </button>
                    <span v-if="!gapMatrix.q3.length" class="text-[10px] text-[var(--color-text-muted)] italic">Tidak ada celah</span>
                  </div>
                </div>

                <!-- Q4: Kolektif (Sedang, Sering) -->
                <div class="bg-white rounded-md border border-zinc-100 p-3 flex flex-col min-h-[110px]">
                  <div class="text-[10px] font-bold text-zinc-600 uppercase tracking-wider mb-2 flex items-center gap-1">
                    <span class="h-1.5 w-1.5 rounded-full bg-zinc-500"></span>
                    4. Kolektif (Umum)
                  </div>
                  <div class="flex flex-wrap gap-1.5 overflow-y-auto">
                    <button v-for="g in gapMatrix.q4" :key="g.originalIndex"
                      @click="selectGap(g.originalIndex)"
                      class="rounded bg-zinc-100 hover:bg-zinc-200 border border-zinc-300 px-2 py-1 text-[10px] font-medium text-zinc-700 text-left transition truncate max-w-full">
                      {{ g.title }}
                    </button>
                    <span v-if="!gapMatrix.q4.length" class="text-[10px] text-[var(--color-text-muted)] italic">Tidak ada celah</span>
                  </div>
                </div>
              </div>

              <!-- X-Axis Label (Horizontal text) -->
              <div class="flex justify-around items-center text-[10px] font-bold text-[var(--color-text-muted)] uppercase tracking-wider pt-2 border-t border-[var(--color-border)] mt-2">
                <span>Bahasan Jarang (Uncommon Method)</span>
                <span class="text-zinc-300">|</span>
                <span>Bahasan Sering (Common Method)</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 1. Topik Dominan -->
        <div v-if="gapData.topik.length" class="mb-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4">
          <div class="flex items-center gap-2 mb-3">
            <div class="flex h-7 w-7 items-center justify-center rounded-md bg-blue-50 text-blue-600">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
            </div>
            <h2 class="text-sm font-medium text-[var(--color-text)]">Topik yang Sudah Banyak Diteliti</h2>
          </div>
          <div v-for="(t, i) in gapData.topik" :key="i" class="mb-2.5 flex gap-2.5 items-start">
            <span class="flex-shrink-0 rounded bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-600">{{ t.count }} paper</span>
            <div>
              <div class="text-sm font-medium text-[var(--color-text)]">{{ t.name }}</div>
              <div class="text-xs text-[var(--color-text-sub)] mt-0.5">{{ t.desc }}</div>
            </div>
          </div>
        </div>

        <!-- 2. Metodologi -->
        <div v-if="gapData.metodologi.length" class="mb-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4">
          <div class="flex items-center gap-2 mb-3">
            <div class="flex h-7 w-7 items-center justify-center rounded-md bg-violet-50 text-violet-600">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>
            </div>
            <h2 class="text-sm font-medium text-[var(--color-text)]">Metodologi yang Dominan</h2>
          </div>
          <div v-for="(m, i) in gapData.metodologi" :key="i" class="mb-2.5 flex gap-2.5 items-start">
            <span class="flex-shrink-0 rounded px-2 py-0.5 text-xs font-medium"
              :class="m.freq === 'Sering' ? 'bg-violet-50 text-violet-600' : 'bg-zinc-100 text-[var(--color-text-sub)]'">{{ m.freq }}</span>
            <div>
              <div class="text-sm font-medium text-[var(--color-text)]">{{ m.name }}</div>
              <div class="text-xs text-[var(--color-text-sub)] mt-0.5">{{ m.desc }}</div>
            </div>
          </div>
        </div>

        <!-- 3. Celah Penelitian -->
        <div v-if="gapData.celah.length" class="mb-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4">
          <div class="flex items-center gap-2 mb-3">
            <div class="flex h-7 w-7 items-center justify-center rounded-md bg-rose-50 text-rose-500">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>
            </div>
            <h2 class="text-sm font-medium text-[var(--color-text)]">Celah Penelitian yang Teridentifikasi</h2>
          </div>
          <div v-for="(g, i) in gapData.celah" :key="i" :id="`gap-card-${i}`"
            class="mb-2 rounded-md border p-3 transition-all duration-300"
            :class="[
              g.priority === 'Tinggi' ? 'border-rose-200 bg-rose-50' : 'border-[var(--color-border)] bg-[var(--color-bg)]',
              activeGapIndex === i ? 'ring-2 ring-[var(--color-primary)] border-transparent scale-[1.01] bg-yellow-50/10 shadow-sm' : ''
            ]">
            <div class="flex items-center gap-1.5 mb-1">
              <span class="text-sm font-medium text-[var(--color-text)]">{{ g.title }}</span>
              <span class="rounded px-1.5 py-0.5 text-[10px] font-medium text-white"
                :class="g.priority === 'Tinggi' ? 'bg-rose-500' : 'bg-amber-500'">Prioritas {{ g.priority }}</span>
            </div>
            <p class="text-xs text-[var(--color-text-sub)] leading-relaxed m-0">{{ g.desc }}</p>
          </div>
        </div>

        <!-- 4. Saran Topik -->
        <div v-if="gapData.saran.length" class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4">
          <div class="flex items-center gap-2 mb-3">
            <div class="flex h-7 w-7 items-center justify-center rounded-md bg-emerald-50 text-emerald-600">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M5 12h14m-7-7l7 7-7 7"/></svg>
            </div>
            <h2 class="text-sm font-medium text-[var(--color-text)]">Saran Topik Riset Lanjutan</h2>
          </div>
          <div v-for="(s, i) in gapData.saran" :key="i"
            class="mb-2 flex gap-2.5 items-start rounded-md bg-emerald-50 border border-emerald-200 px-3 py-2.5">
            <span class="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-emerald-600 text-white text-[10px] font-medium">{{ Number(i) + 1 }}</span>
            <span class="text-sm text-[var(--color-text)] leading-relaxed">{{ s }}</span>
          </div>
        </div>

        <!-- 5. AI Mentor Chat (Diskusi Celah Riset) -->
        <div class="mt-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
          <div class="mb-4 flex items-center justify-between border-b border-[var(--color-border)] pb-3">
            <div class="flex items-center gap-2">
              <div class="flex h-7 w-7 items-center justify-center rounded-md bg-indigo-50 text-indigo-600">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
              </div>
              <div>
                <h2 class="text-sm font-medium text-[var(--color-text)]">Diskusi Celah Riset dengan AI Mentor</h2>
                <p class="text-[10px] text-[var(--color-text-muted)] mt-0.5">Rumuskan judul, masalah penelitian, atau metodologi berdasarkan paper di atas</p>
              </div>
            </div>
            <button @click="clearGapChat" v-if="gapChatMessages.length" class="text-xs font-medium text-red-500 hover:text-red-600 transition">Reset Chat</button>
          </div>

          <!-- Chat Area -->
          <div class="h-64 overflow-y-auto mb-4 border border-[var(--color-border)] rounded-lg bg-zinc-50/50 p-4 space-y-3.5 select-text">
            <div class="rounded-md bg-white border border-zinc-100 p-3 text-xs text-[var(--color-text-sub)] leading-relaxed shadow-sm flex items-start gap-2.5">
              <div class="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded bg-indigo-50 text-indigo-600 text-[10px] font-bold">AI</div>
              <div>
                Halo! Saya adalah mentor riset Anda. Kumpulan paper di atas sudah saya baca. Ada yang bisa saya bantu diskusikan? 
                <div class="mt-2 text-[10px] font-medium text-zinc-400">💡 Anda bisa mengetik sendiri atau klik tombol pintasan di bawah untuk memulai.</div>
              </div>
            </div>

            <div v-for="(msg, idx) in gapChatMessages" :key="idx"
              class="flex gap-2.5 items-start max-w-[85%]"
              :class="msg.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'">
              <div class="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded text-[10px] font-bold"
                :class="msg.role === 'user' ? 'bg-zinc-200 text-zinc-700' : 'bg-indigo-50 text-indigo-600'">
                {{ msg.role === 'user' ? 'U' : 'AI' }}
              </div>
              <div class="rounded-lg p-3 text-xs leading-relaxed shadow-sm whitespace-pre-wrap"
                :class="msg.role === 'user' ? 'bg-[var(--color-primary)] text-white' : 'bg-white text-[var(--color-text)] border border-zinc-200'"
                v-html="parseMarkdown(msg.content)">
              </div>
            </div>

            <div v-if="gapChatLoading" class="flex items-center gap-1.5 text-xs text-[var(--color-text-muted)] p-1">
              <div class="h-3.5 w-3.5 animate-spin rounded-full border border-indigo-600 border-t-transparent"></div>
              <span>AI Mentor sedang menganalisis & menulis...</span>
            </div>

            <div v-if="gapChatError" class="rounded-md bg-red-50 border border-red-100 p-2.5 text-xs text-red-600">
              {{ gapChatError }}
            </div>
          </div>

          <!-- Quick Suggestions Prompts -->
          <div class="mb-4">
            <div class="text-[10px] font-medium uppercase tracking-wider text-[var(--color-text-muted)] mb-2">Pintasan Pertanyaan:</div>
            <div class="flex flex-wrap gap-1.5">
              <button @click="selectQuickPrompt('Buatkan 3 usulan judul penelitian baru yang inovatif untuk menutup Celah Prioritas Tinggi.')"
                class="rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] hover:bg-zinc-50 px-2.5 py-1.5 text-[10px] font-medium text-[var(--color-text-sub)] transition">
                💡 Usulkan Judul Baru
              </button>
              <button @click="selectQuickPrompt('Rumuskan 3 pertanyaan penelitian (research questions) yang tajam untuk celah riset di atas.')"
                class="rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] hover:bg-zinc-50 px-2.5 py-1.5 text-[10px] font-medium text-[var(--color-text-sub)] transition">
                ❓ Rumusan Masalah
              </button>
              <button @click="selectQuickPrompt('Metode penelitian seperti apa yang paling tepat untuk menutup celah riset yang diprioritaskan? Jelaskan langkahnya.')"
                class="rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] hover:bg-zinc-50 px-2.5 py-1.5 text-[10px] font-medium text-[var(--color-text-sub)] transition">
                ⚙️ Saran Metodologi
              </button>
            </div>
          </div>

          <!-- Chat Input Area -->
          <div class="border-t border-[var(--color-border)] pt-3 flex gap-1.5">
            <input v-model="gapChatQuery" type="text" placeholder="Tanyakan saran metodologi, rumusan masalah, atau ide riset..."
              class="flex-1 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-xs outline-none focus:border-[var(--color-primary)]"
              @keyup.enter="sendGapChatMessage" :disabled="gapChatLoading" />
            <button @click="sendGapChatMessage" :disabled="!gapChatQuery.trim() || gapChatLoading"
              class="rounded-md bg-[var(--color-primary)] px-4 py-2 text-xs font-medium text-white transition hover:bg-[var(--color-primary-hover)] disabled:opacity-50">
              Kirim
            </button>
          </div>
        </div>

        <div v-if="gapData.raw" class="mt-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-3.5">
          <details>
            <summary class="text-xs font-medium text-[var(--color-text-muted)] cursor-pointer">Raw AI Response</summary>
            <pre class="mt-2 text-xs text-[var(--color-text-sub)] whitespace-pre-wrap font-mono">{{ gapData.raw }}</pre>
          </details>
        </div>
      </div>

      <div v-else class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] py-16 text-center">
        <svg width="40" height="40" class="mx-auto text-[var(--color-text-muted)]" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24"><path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
        <h3 class="mt-2 text-sm font-medium text-[var(--color-text)]">Belum ada hasil analisis</h3>
        <p class="mt-1 text-sm text-[var(--color-text-sub)]">Pilih paper dan jalankan analisis terlebih dahulu.</p>
      </div>
    </div>
  </div>
</template>
