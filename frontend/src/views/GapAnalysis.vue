<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUploadStore } from '@/stores/upload'
import { useCollectionsStore, type CollectionPaper } from '@/stores/collections'
import { useAIStore } from '@/stores/ai'

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
const hasPapers = computed(() => uploadStore.papers.length > 0 || collectionsStore.collections.length > 0)

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
</script>

<template>
  <div class="p-7 max-w-4xl">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-xl font-extrabold text-[var(--color-text)]">Research Gap Analysis</h1>
        <p class="mt-1 text-[13px] text-[var(--color-text-sub)]">Pilih minimal 3 paper dari upload atau koleksi, lalu analisis celah penelitiannya</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="mb-6 flex gap-1 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-1">
      <button @click="activeTab = 'upload'"
        class="flex-1 rounded-lg py-2.5 text-[13px] font-semibold transition"
        :class="activeTab === 'upload' ? 'bg-[var(--color-primary)] text-white' : 'text-[var(--color-text-sub)] hover:bg-gray-50'">
        Upload PDF
      </button>
      <button @click="activeTab = 'select'"
        class="flex-1 rounded-lg py-2.5 text-[13px] font-semibold transition"
        :class="activeTab === 'select' ? 'bg-[var(--color-primary)] text-white' : 'text-[var(--color-text-sub)] hover:bg-gray-50'">
        Pilih Paper ({{ selectedCount }}/10)
      </button>
      <button @click="activeTab = 'result'" :disabled="!aiStore.gapResult"
        class="flex-1 rounded-lg py-2.5 text-[13px] font-semibold transition disabled:opacity-40"
        :class="activeTab === 'result' ? 'bg-[var(--color-primary)] text-white' : 'text-[var(--color-text-sub)] hover:bg-gray-50'">
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
        class="cursor-pointer rounded-2xl border-2 border-dashed p-12 text-center transition"
        :class="dragOver ? 'border-[var(--color-primary)] bg-[var(--color-primary-soft)]' : 'border-[var(--color-border)] bg-[var(--color-surface)] hover:border-gray-300'">
        <input ref="fileInput" type="file" accept=".pdf" multiple class="hidden" @change="onFileSelect" />
        <div class="text-5xl mb-3">📄</div>
        <h3 class="text-base font-bold text-[var(--color-text)]">
          {{ uploadStore.uploading ? 'Memproses PDF...' : 'Drag & drop PDF di sini' }}
        </h3>
        <p class="mt-1.5 text-[13px] text-[var(--color-text-sub)]">atau klik untuk memilih file (max 50 MB)</p>
        <div v-if="uploadStore.uploading" class="mt-4 flex justify-center">
          <div class="h-8 w-8 animate-spin rounded-full border-3 border-[var(--color-primary)] border-t-transparent"></div>
        </div>
      </div>

      <div v-if="uploadStore.uploadError" class="mt-3 rounded-lg bg-red-50 border border-red-200 px-3.5 py-2.5 text-[13px] text-red-700">
        {{ uploadStore.uploadError }}
      </div>

      <div v-if="uploadStore.papers.length" class="mt-6">
        <h3 class="mb-3 text-sm font-bold text-[var(--color-text)]">Uploaded Papers ({{ uploadStore.papers.length }})</h3>
        <div class="flex flex-col gap-2.5">
          <div v-for="paper in uploadStore.papers" :key="paper.id"
            class="flex items-center justify-between rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-3">
            <div class="min-w-0 flex-1">
              <div class="text-[13.5px] font-semibold text-[var(--color-text)] truncate">{{ paper.title }}</div>
              <div class="text-[12px] text-[var(--color-text-sub)] mt-0.5">
                {{ paper.authors?.join(', ') || 'Unknown' }}
                <span v-if="paper.year"> · {{ paper.year }}</span>
              </div>
            </div>
            <div class="flex items-center gap-2 ml-3 flex-shrink-0">
              <span v-if="isSelected(paper.id)" class="text-[11px] font-semibold text-[var(--color-primary)] bg-[var(--color-primary-soft)] px-2 py-1 rounded-md">Terpilih</span>
              <button @click="uploadStore.deletePaper(paper.id)"
                class="rounded-lg border border-[var(--color-border)] px-2.5 py-1.5 text-[11.5px] text-red-500 hover:bg-red-50 transition">Hapus</button>
            </div>
          </div>
        </div>
      </div>

      <button @click="activeTab = 'select'"
        class="mt-4 w-full rounded-xl bg-[var(--color-primary)] py-3 text-sm font-semibold text-white transition hover:bg-[var(--color-primary-hover)]">
        Lanjut pilih paper →
      </button>
    </div>

    <!-- Tab: Select Papers -->
    <div v-if="activeTab === 'select'">
      <!-- Source Filter -->
      <div class="mb-4 flex flex-wrap items-center gap-2">
        <span class="text-[12px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider">Sumber:</span>
        <button @click="onSourceFilterChange('all')"
          class="rounded-full px-3.5 py-1.5 text-[12px] font-medium transition"
          :class="sourceFilter === 'all' ? 'bg-[var(--color-primary-soft)] text-[var(--color-primary)]' : 'bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-sub)] hover:bg-gray-50'">
          Semua
        </button>
        <button @click="onSourceFilterChange('uploaded')"
          class="rounded-full px-3.5 py-1.5 text-[12px] font-medium transition"
          :class="sourceFilter === 'uploaded' ? 'bg-green-50 text-green-600' : 'bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-sub)] hover:bg-gray-50'">
          📄 Uploaded ({{ uploadStore.papers.length }})
        </button>
        <button v-for="col in collectionsStore.collections" :key="col.id"
          @click="onSourceFilterChange(col.id)"
          class="rounded-full px-3.5 py-1.5 text-[12px] font-medium transition"
          :class="sourceFilter === col.id ? 'bg-purple-50 text-purple-600' : 'bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-sub)] hover:bg-gray-50'">
          📁 {{ col.name }} ({{ col.paper_count || 0 }})
        </button>
      </div>

      <!-- Counter + actions -->
      <div class="mb-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="rounded-lg px-3 py-1.5 text-[13px] font-semibold"
            :class="canAnalyze ? 'bg-[var(--color-primary-soft)] text-[var(--color-primary)]' : 'bg-gray-100 text-[var(--color-text-muted)]'">
            {{ selectedCount }} / 10 dipilih
          </div>
          <span class="text-[12px] text-[var(--color-text-sub)]">Minimal 3 paper</span>
        </div>
        <div class="flex gap-2">
          <button @click="selectAll" class="rounded-lg border border-[var(--color-border)] px-3 py-1.5 text-[11.5px] text-[var(--color-text-sub)] hover:bg-gray-50 transition">Pilih Semua</button>
          <button @click="deselectAll" class="rounded-lg border border-[var(--color-border)] px-3 py-1.5 text-[11.5px] text-[var(--color-text-sub)] hover:bg-gray-50 transition">Reset</button>
        </div>
      </div>

      <!-- Progress bar -->
      <div class="mb-4 h-1.5 w-full rounded-full bg-gray-100">
        <div class="h-full rounded-full transition-all duration-300"
          :style="{ width: `${(selectedCount / 10) * 100}%` }"
          :class="canAnalyze ? 'bg-[var(--color-primary)]' : 'bg-gray-300'"></div>
      </div>

      <!-- Loading -->
      <div v-if="loadingCollection" class="flex justify-center py-8">
        <div class="h-7 w-7 animate-spin rounded-full border-3 border-[var(--color-primary)] border-t-transparent"></div>
      </div>

      <!-- Paper Grid -->
      <div v-else-if="allPapers.length" class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div v-for="paper in allPapers" :key="paper.id"
          @click="togglePaper(paper.id)"
          class="cursor-pointer rounded-xl border-2 p-4 transition"
          :class="isSelected(paper.id) ? 'border-[var(--color-primary)] bg-[var(--color-primary-soft)]' : 'border-[var(--color-border)] bg-[var(--color-surface)] hover:border-gray-300'">
          <div class="flex items-start gap-3">
            <div class="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-md border-2 transition"
              :class="isSelected(paper.id) ? 'border-[var(--color-primary)] bg-[var(--color-primary)]' : 'border-gray-300'">
              <svg v-if="isSelected(paper.id)" width="12" height="12" fill="none" stroke="white" stroke-width="2.5" viewBox="0 0 24 24">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1.5 mb-1">
                <span class="rounded-full px-1.5 py-0.5 text-[9px] font-semibold"
                  :class="paper.source === 'uploaded' ? 'bg-green-50 text-green-600' : 'bg-purple-50 text-purple-600'">
                  {{ paper.source_label }}
                </span>
              </div>
              <div class="text-[13.5px] font-semibold text-[var(--color-text)] leading-snug line-clamp-2">{{ paper.title }}</div>
              <div class="text-[11.5px] text-[var(--color-text-sub)] mt-1.5">
                {{ formatAuthors(paper.authors) }}
              </div>
              <div class="flex gap-3 mt-2 text-[11px] text-[var(--color-text-muted)]">
                <span v-if="paper.year">{{ paper.year }}</span>
                <span v-if="paper.page_count">{{ paper.page_count }} hal</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty -->
      <div v-else class="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] py-12 text-center">
        <div class="text-4xl mb-2">📄</div>
        <p class="text-[13px] text-[var(--color-text-sub)]">
          Belum ada paper. Upload PDF atau simpan paper dari pencarian ke koleksi terlebih dahulu.
        </p>
        <div class="mt-4 flex justify-center gap-2">
          <button @click="activeTab = 'upload'" class="rounded-xl bg-[var(--color-primary)] px-4 py-2 text-[13px] font-semibold text-white">Upload PDF</button>
          <router-link to="/search" class="rounded-xl border border-[var(--color-border)] px-4 py-2 text-[13px] font-medium text-[var(--color-text-sub)] hover:bg-gray-50 transition">Cari Paper</router-link>
        </div>
      </div>

      <!-- Analyze Button -->
      <button @click="runAnalysis" :disabled="!canAnalyze"
        class="mt-6 flex w-full items-center justify-center gap-2 rounded-xl py-3.5 text-sm font-semibold transition"
        :class="canAnalyze ? 'bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)]' : 'bg-gray-100 text-gray-400 cursor-not-allowed'">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        Analisis Research Gap ({{ selectedCount }} paper)
      </button>
    </div>

    <!-- Tab: Results (unchanged) -->
    <div v-if="activeTab === 'result'">
      <!-- Loading -->
      <div v-if="aiStore.loading" class="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] py-20 text-center">
        <div class="flex justify-center mb-4">
          <div class="h-10 w-10 animate-spin rounded-full border-4 border-[var(--color-primary)] border-t-transparent"></div>
        </div>
        <h3 class="text-base font-bold text-[var(--color-text)]">AI sedang menganalisis...</h3>
        <p class="mt-1.5 text-[13px] text-[var(--color-text-sub)]">Membaca {{ selectedCount }} paper dan mengidentifikasi celah penelitian</p>
      </div>

      <div v-else-if="gapData">
        <div class="mb-5 rounded-xl bg-gradient-to-r from-[var(--color-primary-soft)] to-purple-50 border border-blue-100 px-5 py-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <svg width="20" height="20" fill="none" stroke="var(--color-primary)" stroke-width="1.5" viewBox="0 0 24 24">
              <path d="M12 3v1m0 16v1m-8-9H3m18 0h-1m-2.636-6.364l-.707.707M6.343 17.657l-.707.707m0-12.728l.707.707m11.314 11.314l.707.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
            </svg>
            <div>
              <div class="text-[14px] font-bold text-[var(--color-text)]">Analisis Selesai</div>
              <div class="text-[12px] text-[var(--color-text-sub)]">Berdasarkan {{ selectedCount }} paper · Powered by Groq AI</div>
            </div>
          </div>
          <button @click="resetAnalysis" class="rounded-lg border border-[var(--color-border)] bg-white px-3 py-1.5 text-[12px] font-medium text-[var(--color-text-sub)] hover:bg-gray-50 transition">Analisis Ulang</button>
        </div>

        <!-- 1. Topik Dominan -->
        <div v-if="gapData.topik.length" class="mb-4 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
          <div class="flex items-center gap-2.5 mb-4">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--color-primary-soft)] text-[var(--color-primary)]">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
            </div>
            <h2 class="text-[15px] font-bold text-[var(--color-text)]">Topik yang Sudah Banyak Diteliti</h2>
          </div>
          <div v-for="(t, i) in gapData.topik" :key="i" class="mb-3 flex gap-3 items-start">
            <span class="flex-shrink-0 rounded-full bg-[var(--color-primary-soft)] px-2.5 py-0.5 text-[11px] font-bold text-[var(--color-primary)]">{{ t.count }} paper</span>
            <div>
              <div class="text-[13.5px] font-semibold text-[var(--color-text)]">{{ t.name }}</div>
              <div class="text-[12.5px] text-[var(--color-text-sub)] mt-0.5">{{ t.desc }}</div>
            </div>
          </div>
        </div>

        <!-- 2. Metodologi -->
        <div v-if="gapData.metodologi.length" class="mb-4 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
          <div class="flex items-center gap-2.5 mb-4">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-50 text-purple-600">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>
            </div>
            <h2 class="text-[15px] font-bold text-[var(--color-text)]">Metodologi yang Dominan</h2>
          </div>
          <div v-for="(m, i) in gapData.metodologi" :key="i" class="mb-3 flex gap-3 items-start">
            <span class="flex-shrink-0 rounded-full px-2.5 py-0.5 text-[11px] font-bold"
              :class="m.freq === 'Sering' ? 'bg-purple-50 text-purple-600' : 'bg-gray-100 text-[var(--color-text-sub)]'">{{ m.freq }}</span>
            <div>
              <div class="text-[13.5px] font-semibold text-[var(--color-text)]">{{ m.name }}</div>
              <div class="text-[12.5px] text-[var(--color-text-sub)] mt-0.5">{{ m.desc }}</div>
            </div>
          </div>
        </div>

        <!-- 3. Celah Penelitian -->
        <div v-if="gapData.celah.length" class="mb-4 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
          <div class="flex items-center gap-2.5 mb-4">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-red-50 text-red-500">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>
            </div>
            <h2 class="text-[15px] font-bold text-[var(--color-text)]">Celah Penelitian yang Teridentifikasi</h2>
          </div>
          <div v-for="(g, i) in gapData.celah" :key="i"
            class="mb-3 rounded-xl border p-4"
            :class="g.priority === 'Tinggi' ? 'border-red-200 bg-red-50' : 'border-[var(--color-border)] bg-[var(--color-bg)]'">
            <div class="flex items-center gap-2 mb-1.5">
              <span class="text-[13.5px] font-semibold text-[var(--color-text)]">{{ g.title }}</span>
              <span class="rounded-full px-2 py-0.5 text-[10px] font-bold text-white"
                :class="g.priority === 'Tinggi' ? 'bg-red-500' : 'bg-orange-400'">Prioritas {{ g.priority }}</span>
            </div>
            <p class="text-[12.5px] text-[var(--color-text-sub)] leading-relaxed m-0">{{ g.desc }}</p>
          </div>
        </div>

        <!-- 4. Saran Topik -->
        <div v-if="gapData.saran.length" class="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
          <div class="flex items-center gap-2.5 mb-4">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-green-50 text-green-600">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M5 12h14m-7-7l7 7-7 7"/></svg>
            </div>
            <h2 class="text-[15px] font-bold text-[var(--color-text)]">Saran Topik Riset Lanjutan</h2>
          </div>
          <div v-for="(s, i) in gapData.saran" :key="i"
            class="mb-2.5 flex gap-3 items-start rounded-xl bg-green-50 border border-green-200 px-4 py-3">
            <span class="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-green-600 text-white text-[11px] font-bold">{{ i + 1 }}</span>
            <span class="text-[13px] text-[var(--color-text)] leading-relaxed">{{ s }}</span>
          </div>
        </div>

        <div v-if="gapData.raw" class="mt-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-bg)] p-4">
          <details>
            <summary class="text-[12px] font-medium text-[var(--color-text-muted)] cursor-pointer">Raw AI Response</summary>
            <pre class="mt-2 text-[11px] text-[var(--color-text-sub)] whitespace-pre-wrap font-mono">{{ gapData.raw }}</pre>
          </details>
        </div>
      </div>

      <div v-else class="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] py-20 text-center">
        <div class="text-5xl mb-3">💡</div>
        <h3 class="text-base font-bold">Belum ada hasil analisis</h3>
        <p class="mt-1 text-[13px] text-[var(--color-text-sub)]">Pilih paper dan jalankan analisis terlebih dahulu.</p>
      </div>
    </div>
  </div>
</template>
