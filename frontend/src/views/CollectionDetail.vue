<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCollectionsStore, type CollectionDetail, type CollectionPaper } from '@/stores/collections'
import { useAIStore } from '@/stores/ai'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const collectionsStore = useCollectionsStore()
const aiStore = useAIStore()

const collectionId = route.params.id as string
const collection = ref<CollectionDetail | null>(null)
const loading = ref(true)
const error = ref('')

// Notes editing
const editingNotes = ref<string | null>(null)
const notesText = ref('')

// Gap analysis selection
const selectedIds = ref<Set<string>>(new Set())

// Bibliography export state
const showBibModal = ref(false)
const bibFormat = ref<'APA' | 'IEEE' | 'Chicago'>('APA')
const bibEntries = ref<string[]>([])
const loadingBib = ref(false)
const bibError = ref('')
const copySuccess = ref(false)

async function generateBibliography() {
  if (!collection.value?.papers.length) return
  loadingBib.value = true
  bibError.value = ''
  try {
    const paperIds = collection.value.papers.map(p => p.id)
    const { data } = await api.post('/bibliography/generate', {
      paper_ids: paperIds,
      format: bibFormat.value
    })
    bibEntries.value = data.entries
    showBibModal.value = true
  } catch (err: any) {
    bibError.value = err.response?.data?.detail || 'Gagal menghasilkan daftar pustaka'
  } finally {
    loadingBib.value = false
  }
}

function copyBibToClipboard() {
  const text = bibEntries.value.join('\n\n')
  navigator.clipboard.writeText(text).then(() => {
    copySuccess.value = true
    setTimeout(() => { copySuccess.value = false }, 2000)
  })
}

function downloadBibAsTxt() {
  const text = bibEntries.value.join('\n\n')
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `daftar_pustaka_${collection.value?.name.toLowerCase().replace(/\s+/g, '_') || 'export'}.txt`
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  await fetchCollection()
})

async function fetchCollection() {
  loading.value = true
  error.value = ''
  try {
    collection.value = await collectionsStore.fetchCollectionDetail(collectionId)
    if (!collection.value) error.value = 'Koleksi tidak ditemukan'
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Gagal memuat koleksi'
  } finally {
    loading.value = false
  }
}

function togglePaper(id: string) {
  const s = new Set(selectedIds.value)
  if (s.has(id)) s.delete(id)
  else s.add(id)
  selectedIds.value = s
}

function isSelected(id: string): boolean {
  return selectedIds.value.has(id)
}

async function removePaper(paperId: string) {
  if (!confirm('Hapus paper dari koleksi ini?')) return
  await collectionsStore.removePaperFromCollection(collectionId, paperId)
  await fetchCollection()
}

function startEditNotes(paper: CollectionPaper) {
  editingNotes.value = paper.id
  notesText.value = paper.notes || ''
}

async function saveNotes(paperId: string) {
  await collectionsStore.updatePaperNotes(collectionId, paperId, notesText.value)
  editingNotes.value = null
  await fetchCollection()
}

async function runGapAnalysis() {
  if (selectedIds.value.size < 3) return
  await aiStore.analyzeGaps(Array.from(selectedIds.value))
  router.push('/gap-analysis')
}

function formatAuthors(authors: string[]): string {
  if (!authors?.length) return 'Unknown'
  if (authors.length <= 3) return authors.join(', ')
  return `${authors.slice(0, 3).join(', ')} et al.`
}

function goBack() {
  router.push('/collections')
}
</script>

<template>
  <div class="px-6 py-5 w-full">
    <!-- Back -->
    <button @click="goBack" class="mb-4 inline-flex items-center gap-1 text-sm text-[var(--color-text-sub)] hover:text-[var(--color-primary)] transition">
      <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M19 12H5m7-7l-7 7 7 7"/></svg>
      Semua Collections
    </button>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="h-6 w-6 animate-spin rounded-full border-2 border-[var(--color-primary)] border-t-transparent"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="rounded-lg border border-red-200 bg-red-50 p-5 text-center">
      <p class="text-sm font-medium text-red-700">{{ error }}</p>
      <button @click="fetchCollection" class="mt-2 rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white">Coba Lagi</button>
    </div>

    <!-- Collection Detail -->
    <div v-else-if="collection">
      <!-- Header -->
      <div class="flex items-start justify-between mb-5">
        <div>
          <div class="flex items-center gap-2.5 mb-0.5">
            <div class="flex h-8 w-8 items-center justify-center rounded-md bg-[var(--color-primary-soft)] text-[var(--color-primary)]">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>
            </div>
            <h1 class="text-lg font-semibold text-[var(--color-text)]">{{ collection.name }}</h1>
          </div>
          <p v-if="collection.description" class="text-sm text-[var(--color-text-sub)] ml-[42px]">{{ collection.description }}</p>
          <p class="text-xs text-[var(--color-text-muted)] mt-0.5 ml-[42px]">{{ collection.paper_count }} paper</p>
        </div>
        <div class="flex items-center gap-2">
          <button v-if="collection.papers.length > 0" @click="generateBibliography"
            :disabled="loadingBib"
            class="flex items-center gap-1.5 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-3.5 py-2 text-sm font-medium text-[var(--color-text-sub)] transition hover:bg-zinc-50 disabled:opacity-50">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
            {{ loadingBib ? 'Mengekspor...' : 'Export Bibliography' }}
          </button>
          <button v-if="collection.papers.length >= 3" @click="runGapAnalysis"
            :disabled="selectedIds.size < 3"
            class="flex items-center gap-1.5 rounded-md bg-violet-600 px-3.5 py-2 text-sm font-medium text-white transition hover:bg-violet-700 disabled:opacity-50">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
            Gap Analysis ({{ selectedIds.size }})
          </button>
        </div>
      </div>

      <!-- Empty collection -->
      <div v-if="!collection.papers.length" class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] py-12 text-center">
        <svg width="40" height="40" class="mx-auto text-[var(--color-text-muted)]" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        <h3 class="mt-3 text-sm font-medium text-[var(--color-text)]">Koleksi ini masih kosong</h3>
        <p class="mt-1 text-sm text-[var(--color-text-sub)]">Simpan paper dari halaman pencarian atau detail paper.</p>
        <router-link to="/search"
          class="mt-3 inline-block rounded-md bg-[var(--color-primary)] px-4 py-1.5 text-sm font-medium text-white transition hover:bg-[var(--color-primary-hover)]">
          Cari Paper
        </router-link>
      </div>

      <!-- Papers list -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4">
        <div v-for="paper in collection.papers" :key="paper.id"
          class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 transition hover:border-zinc-300">
          <div class="flex items-start gap-2.5">
            <!-- Checkbox for gap analysis -->
            <div v-if="collection.paper_count >= 3"
              @click.stop="togglePaper(paper.id)"
              class="mt-0.5 flex h-4 w-4 flex-shrink-0 cursor-pointer items-center justify-center rounded border transition"
              :class="isSelected(paper.id) ? 'border-[var(--color-primary)] bg-[var(--color-primary)]' : 'border-zinc-300'">
              <svg v-if="isSelected(paper.id)" width="10" height="10" fill="none" stroke="white" stroke-width="2.5" viewBox="0 0 24 24">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>

            <!-- Paper content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-1.5 mb-0.5">
                <span class="rounded px-1.5 py-0.5 text-[10px] font-medium"
                  :class="paper.source === 'arxiv' ? 'bg-violet-50 text-violet-600' : paper.source === 'uploaded' ? 'bg-emerald-50 text-emerald-600' : 'bg-blue-50 text-blue-600'">
                  {{ paper.source === 'semantic_scholar' ? 'S2' : paper.source === 'arxiv' ? 'arXiv' : 'Upload' }}
                </span>
                <span v-if="paper.year" class="text-xs text-[var(--color-text-muted)]">{{ paper.year }}</span>
              </div>

              <router-link :to="`/papers/${paper.id}`" class="text-sm font-medium leading-snug text-[var(--color-text)] hover:text-[var(--color-primary)] transition">
                {{ paper.title }}
              </router-link>

              <p class="mt-0.5 text-xs text-[var(--color-text-sub)]">{{ formatAuthors(paper.authors) }}</p>

              <p v-if="paper.abstract" class="mt-1.5 line-clamp-2 text-xs leading-relaxed text-[var(--color-text-sub)]">{{ paper.abstract }}</p>

              <!-- Notes -->
              <div v-if="editingNotes === paper.id" class="mt-2.5">
                <textarea v-model="notesText" rows="2" placeholder="Tambahkan catatan..."
                  class="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-2.5 py-1.5 text-xs outline-none resize-none focus:border-[var(--color-primary)]"></textarea>
                <div class="mt-1 flex gap-1.5">
                  <button @click="saveNotes(paper.id)" class="rounded-md bg-[var(--color-primary)] px-2.5 py-1 text-xs font-medium text-white">Simpan</button>
                  <button @click="editingNotes = null" class="rounded-md border border-[var(--color-border)] px-2.5 py-1 text-xs text-[var(--color-text-sub)]">Batal</button>
                </div>
              </div>
              <div v-else-if="paper.notes" class="mt-2 rounded-md bg-[var(--color-bg)] border-l-2 border-[var(--color-primary)] px-2.5 py-1.5">
                <p class="text-xs text-[var(--color-text-sub)]">{{ paper.notes }}</p>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex flex-col gap-1 flex-shrink-0">
              <button @click="startEditNotes(paper)" v-if="editingNotes !== paper.id"
                class="rounded-md border border-[var(--color-border)] px-2 py-1 text-xs text-[var(--color-text-sub)] transition hover:bg-zinc-50">
                <svg width="12" height="12" class="inline mr-0.5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M17 3a2.83 2.83 0 114 4L7.5 20.5 2 22l1.5-5.5z"/></svg>
                Catatan
              </button>
              <button @click="removePaper(paper.id)"
                class="rounded-md border border-[var(--color-border)] px-2 py-1 text-xs text-red-500 transition hover:bg-red-50">
                <svg width="12" height="12" class="inline mr-0.5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6m5 0V4a1 1 0 011-1h2a1 1 0 011 1v2"/></svg>
                Hapus
              </button>
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>

    <!-- Bibliography Modal -->
    <div v-if="showBibModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div class="w-full max-w-2xl rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-5 shadow-xl animate-fade-in">
        <div class="flex items-center justify-between border-b border-[var(--color-border)] pb-3 mb-4">
          <div class="flex items-center gap-2">
            <svg width="16" height="16" class="text-[var(--color-primary)]" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
            <h3 class="text-sm font-semibold text-[var(--color-text)]">Export Bibliography</h3>
          </div>
          <button @click="showBibModal = false" class="text-[var(--color-text-muted)] hover:text-[var(--color-text)] text-lg leading-none">×</button>
        </div>

        <div v-if="bibError" class="mb-3 rounded-md bg-red-50 px-2.5 py-1.5 text-xs text-red-600">
          {{ bibError }}
        </div>

        <div class="mb-4 flex items-center justify-between">
          <div class="flex gap-1 bg-[var(--color-bg)] rounded-md border border-[var(--color-border)] p-0.5">
            <button v-for="fmt in ['APA', 'IEEE', 'Chicago']" :key="fmt"
              @click="bibFormat = fmt as any; generateBibliography()"
              class="rounded px-3 py-1 text-xs font-medium transition"
              :class="bibFormat === fmt ? 'bg-[var(--color-surface)] text-[var(--color-text)] shadow-sm' : 'text-[var(--color-text-sub)] hover:text-[var(--color-text)]'">
              {{ fmt }}
            </button>
          </div>

          <div class="flex gap-2">
            <button @click="copyBibToClipboard"
              class="rounded-md bg-[var(--color-primary)] px-3 py-1.5 text-xs font-medium text-white transition hover:bg-[var(--color-primary-hover)]">
              {{ copySuccess ? 'Copied!' : 'Copy All' }}
            </button>
            <button @click="downloadBibAsTxt"
              class="rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-1.5 text-xs font-medium text-[var(--color-text-sub)] transition hover:bg-zinc-50">
              Download .TXT
            </button>
          </div>
        </div>

        <!-- Bibliography Content -->
        <div class="max-h-96 overflow-y-auto rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] p-4 font-mono text-xs text-[var(--color-text-sub)] leading-relaxed select-text whitespace-pre-wrap">
          <div v-for="(entry, index) in bibEntries" :key="index" class="mb-3 last:mb-0">
            {{ entry }}
          </div>
          <div v-if="!bibEntries.length" class="text-center text-[var(--color-text-muted)] py-4">
            Tidak ada entri yang dihasilkan.
          </div>
        </div>
      </div>
    </div>
</template>
