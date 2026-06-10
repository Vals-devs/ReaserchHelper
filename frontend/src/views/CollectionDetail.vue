<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCollectionsStore, type CollectionDetail, type CollectionPaper } from '@/stores/collections'
import { useAIStore } from '@/stores/ai'

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
  <div class="p-7 max-w-4xl">
    <!-- Back -->
    <button @click="goBack" class="mb-5 inline-flex items-center gap-1.5 text-[13px] text-[var(--color-text-sub)] hover:text-[var(--color-primary)] transition">
      ← Semua Collections
    </button>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="h-8 w-8 animate-spin rounded-full border-3 border-[var(--color-primary)] border-t-transparent"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-6 text-center">
      <p class="text-[14px] font-semibold text-red-700">{{ error }}</p>
      <button @click="fetchCollection" class="mt-3 rounded-lg bg-red-600 px-4 py-2 text-[13px] font-semibold text-white">Coba Lagi</button>
    </div>

    <!-- Collection Detail -->
    <div v-else-if="collection">
      <!-- Header -->
      <div class="flex items-start justify-between mb-6">
        <div>
          <div class="flex items-center gap-3 mb-1">
            <span class="text-2xl">📁</span>
            <h1 class="text-xl font-extrabold text-[var(--color-text)]">{{ collection.name }}</h1>
          </div>
          <p v-if="collection.description" class="text-[13px] text-[var(--color-text-sub)] ml-10">{{ collection.description }}</p>
          <p class="text-[12px] text-[var(--color-text-muted)] mt-1 ml-10">{{ collection.paper_count }} paper</p>
        </div>
        <button v-if="collection.paper_count >= 3" @click="runGapAnalysis"
          :disabled="selectedIds.size < 3"
          class="flex items-center gap-2 rounded-xl bg-purple-600 px-4 py-2.5 text-[13px] font-semibold text-white transition hover:bg-purple-700 disabled:opacity-50">
          💡 Gap Analysis ({{ selectedIds.size }})
        </button>
      </div>

      <!-- Empty collection -->
      <div v-if="!collection.papers.length" class="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] py-16 text-center">
        <div class="text-5xl">📄</div>
        <h3 class="mt-3 text-base font-semibold">Koleksi ini masih kosong</h3>
        <p class="mt-1 text-[13px] text-[var(--color-text-sub)]">Simpan paper dari halaman pencarian atau detail paper.</p>
        <router-link to="/search"
          class="mt-4 inline-block rounded-xl bg-[var(--color-primary)] px-5 py-2 text-[13px] font-semibold text-white transition hover:bg-[var(--color-primary-hover)]">
          Cari Paper
        </router-link>
      </div>

      <!-- Papers list -->
      <div v-else class="flex flex-col gap-3">
        <div v-for="paper in collection.papers" :key="paper.id"
          class="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5 transition hover:border-[var(--color-primary)]">
          <div class="flex items-start gap-3">
            <!-- Checkbox for gap analysis -->
            <div v-if="collection.paper_count >= 3"
              @click.stop="togglePaper(paper.id)"
              class="mt-1 flex h-5 w-5 flex-shrink-0 cursor-pointer items-center justify-center rounded-md border-2 transition"
              :class="isSelected(paper.id) ? 'border-[var(--color-primary)] bg-[var(--color-primary)]' : 'border-gray-300'">
              <svg v-if="isSelected(paper.id)" width="12" height="12" fill="none" stroke="white" stroke-width="2.5" viewBox="0 0 24 24">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>

            <!-- Paper content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="rounded-full px-2 py-0.5 text-[10px] font-semibold"
                  :class="paper.source === 'arxiv' ? 'bg-purple-50 text-purple-600' : paper.source === 'uploaded' ? 'bg-green-50 text-green-600' : 'bg-[var(--color-primary-soft)] text-[var(--color-primary)]'">
                  {{ paper.source === 'semantic_scholar' ? 'S2' : paper.source === 'arxiv' ? 'arXiv' : 'Upload' }}
                </span>
                <span v-if="paper.year" class="text-[11px] text-[var(--color-text-muted)]">{{ paper.year }}</span>
              </div>

              <router-link :to="`/papers/${paper.id}`" class="text-[14px] font-bold leading-snug text-[var(--color-text)] hover:text-[var(--color-primary)] transition">
                {{ paper.title }}
              </router-link>

              <p class="mt-1 text-[12.5px] text-[var(--color-text-sub)]">{{ formatAuthors(paper.authors) }}</p>

              <p v-if="paper.abstract" class="mt-2 line-clamp-2 text-[12.5px] leading-relaxed text-[var(--color-text-sub)]">{{ paper.abstract }}</p>

              <!-- Notes -->
              <div v-if="editingNotes === paper.id" class="mt-3">
                <textarea v-model="notesText" rows="2" placeholder="Tambahkan catatan..."
                  class="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-[12.5px] outline-none resize-none focus:border-[var(--color-primary)]"></textarea>
                <div class="mt-1.5 flex gap-2">
                  <button @click="saveNotes(paper.id)" class="rounded-lg bg-[var(--color-primary)] px-3 py-1 text-[11px] font-semibold text-white">Simpan</button>
                  <button @click="editingNotes = null" class="rounded-lg border border-[var(--color-border)] px-3 py-1 text-[11px] text-[var(--color-text-sub)]">Batal</button>
                </div>
              </div>
              <div v-else-if="paper.notes" class="mt-2.5 rounded-lg bg-[var(--color-bg)] border-l-3 border-[var(--color-primary)] px-3 py-2">
                <p class="text-[12px] text-[var(--color-text-sub)]">📝 {{ paper.notes }}</p>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex flex-col gap-1.5 flex-shrink-0">
              <button @click="startEditNotes(paper)" v-if="editingNotes !== paper.id"
                class="rounded-lg border border-[var(--color-border)] px-2.5 py-1.5 text-[11px] text-[var(--color-text-sub)] transition hover:bg-gray-50">
                📝 Catatan
              </button>
              <button @click="removePaper(paper.id)"
                class="rounded-lg border border-[var(--color-border)] px-2.5 py-1.5 text-[11px] text-red-500 transition hover:bg-red-50">
                🗑 Hapus
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
