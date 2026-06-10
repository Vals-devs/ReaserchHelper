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

// Explain text state
const explainText = ref('')
const explainResult = ref('')
const explainLoading = ref(false)

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
</script>

<template>
  <div class="p-7 max-w-5xl">
    <!-- Back button -->
    <button @click="goBack" class="mb-5 inline-flex items-center gap-1.5 text-[13px] text-[var(--color-text-sub)] hover:text-[var(--color-primary)] transition">
      ← Kembali ke hasil pencarian
    </button>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center gap-3 py-20">
      <div class="h-8 w-8 animate-spin rounded-full border-3 border-[var(--color-primary)] border-t-transparent"></div>
      <span class="text-[13px] text-[var(--color-text-muted)]">Memuat detail paper...</span>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-6 text-center">
      <div class="text-3xl mb-2">😕</div>
      <p class="text-[14px] font-semibold text-red-700">{{ error }}</p>
      <button @click="fetchPaper" class="mt-3 rounded-lg bg-red-600 px-4 py-2 text-[13px] font-semibold text-white hover:bg-red-700 transition">Coba Lagi</button>
    </div>

    <!-- Success toast -->
    <div v-if="saveSuccess" class="fixed top-4 right-4 z-50 rounded-xl bg-green-600 px-4 py-2.5 text-[13px] font-semibold text-white shadow-lg">
      ✅ {{ saveSuccess }}
    </div>

    <!-- Paper Detail -->
    <div v-else-if="paper" class="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-6 items-start">
      <!-- Left: Paper Info -->
      <div>
        <!-- Header Card -->
        <div class="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-7">
          <div class="flex flex-wrap items-center gap-2 mb-3">
            <span class="rounded-full px-2.5 py-0.5 text-[11px] font-semibold"
              :class="paper.source === 'arxiv' ? 'bg-purple-50 text-purple-600' : paper.source === 'uploaded' ? 'bg-green-50 text-green-600' : 'bg-[var(--color-primary-soft)] text-[var(--color-primary)]'">
              {{ paper.source === 'semantic_scholar' ? 'Semantic Scholar' : paper.source === 'arxiv' ? 'arXiv' : 'Uploaded' }}
            </span>
            <span v-if="paper.year" class="text-[12px] text-[var(--color-text-muted)]">{{ paper.year }}</span>
            <span v-for="field in (paper.fields_of_study || []).slice(0, 3)" :key="field"
              class="rounded-md bg-green-50 px-2 py-0.5 text-[11px] font-medium text-green-600">{{ field }}</span>
          </div>

          <h1 class="text-[22px] font-extrabold leading-tight text-[var(--color-text)]">{{ paper.title }}</h1>
          <p class="mt-3 text-[13.5px] leading-relaxed text-[var(--color-text-sub)]">{{ formatAuthors(paper.authors) }}</p>

          <div class="mt-5 flex flex-wrap items-center gap-4 border-t border-[var(--color-border)] pt-4">
            <div v-if="paper.citation_count" class="flex items-center gap-1.5 text-[13px] text-[var(--color-text-sub)]">
              📎 <strong class="text-[var(--color-text)]">{{ paper.citation_count.toLocaleString() }}</strong> sitasi
            </div>
            <a v-if="paper.doi" :href="`https://doi.org/${paper.doi}`" target="_blank"
              class="flex items-center gap-1.5 text-[13px] text-[var(--color-primary)] hover:underline">
              🔗 DOI: {{ paper.doi }}
            </a>
            <span v-if="paper.page_count" class="text-[13px] text-[var(--color-text-muted)]">📄 {{ paper.page_count }} halaman</span>
          </div>

          <!-- Action Buttons -->
          <div class="mt-5 flex flex-wrap gap-2.5">
            <button @click="handleSummarize"
              class="flex items-center gap-2 rounded-xl bg-[var(--color-primary)] px-4 py-2.5 text-[13px] font-semibold text-white transition hover:bg-[var(--color-primary-hover)]">
              ✨ AI Summarize
            </button>
            <button @click="showSaveModal = !showSaveModal"
              class="flex items-center gap-2 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-2.5 text-[13px] font-medium text-[var(--color-text-sub)] transition hover:bg-gray-50">
              📚 Simpan ke Koleksi
            </button>
            <button @click="fetchRelated" :disabled="loadingRelated"
              class="flex items-center gap-2 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-2.5 text-[13px] font-medium text-[var(--color-text-sub)] transition hover:bg-gray-50 disabled:opacity-50">
              🔍 {{ loadingRelated ? 'Mencari...' : 'Find Related' }}
            </button>
            <a v-if="paper.url" :href="paper.url" target="_blank"
              class="flex items-center gap-2 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-2.5 text-[13px] font-medium text-[var(--color-text-sub)] transition hover:bg-gray-50">
              Buka Paper ↗
            </a>
          </div>

          <!-- Save to Collection Modal -->
          <div v-if="showSaveModal" class="mt-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-bg)] p-4">
            <h4 class="text-[13px] font-bold text-[var(--color-text)] mb-3">Pilih Koleksi:</h4>
            <div v-if="saveError" class="mb-2 rounded-lg bg-red-50 px-3 py-2 text-[12px] text-red-600">{{ saveError }}</div>
            <!-- Existing collections -->
            <div v-if="collectionsStore.collections.length" class="flex flex-col gap-1.5 mb-3">
              <button v-for="col in collectionsStore.collections" :key="col.id"
                @click="saveToCollection(col.id)" :disabled="savingToCollection"
                class="flex items-center justify-between rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 text-left text-[12.5px] transition hover:border-[var(--color-primary)] disabled:opacity-50">
                <span class="font-medium text-[var(--color-text)]">{{ col.name }}</span>
                <span class="text-[11px] text-[var(--color-text-muted)]">Simpan →</span>
              </button>
            </div>
            <div v-else class="mb-3 text-[12px] text-[var(--color-text-muted)]">Belum ada koleksi.</div>
            <!-- Create new -->
            <div class="border-t border-[var(--color-border)] pt-3">
              <label class="text-[11px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider">Buat Koleksi Baru</label>
              <div class="mt-1.5 flex gap-2">
                <input v-model="newCollectionName" type="text" placeholder="Nama koleksi..."
                  class="flex-1 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 text-[12.5px] outline-none focus:border-[var(--color-primary)]"
                  @keyup.enter="createAndSave" />
                <button @click="createAndSave" :disabled="!newCollectionName.trim() || savingToCollection"
                  class="rounded-lg bg-[var(--color-primary)] px-3 py-2 text-[12px] font-semibold text-white disabled:opacity-50 transition hover:bg-[var(--color-primary-hover)]">
                  {{ savingToCollection ? '...' : 'Buat & Simpan' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Abstract -->
        <div v-if="paper.abstract" class="mt-4 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-7">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-[15px] font-bold text-[var(--color-text)]">Abstrak</h2>
            <button @click="translateAbstract" :disabled="translatingAbstract || !!translatedAbstract"
              class="flex items-center gap-1.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-1.5 text-[11.5px] font-medium text-[var(--color-text-sub)] transition hover:bg-gray-50 disabled:opacity-50">
              {{ translatingAbstract ? 'Menerjemahkan...' : translatedAbstract ? '✅ Sudah diterjemahkan' : '🌐 Terjemahkan ke Indonesia' }}
            </button>
          </div>
          <p class="text-[14px] leading-[1.75] text-[var(--color-text-sub)] whitespace-pre-line">{{ paper.abstract }}</p>

          <!-- Translated Abstract -->
          <div v-if="translatedAbstract" class="mt-4 rounded-xl bg-blue-50 border border-blue-200 p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-[10px] font-bold uppercase tracking-wider text-blue-600">🇮🇩 Terjemahan (AI)</span>
            </div>
            <p class="text-[13.5px] leading-[1.7] text-[var(--color-text)] whitespace-pre-line">{{ translatedAbstract }}</p>
          </div>
        </div>

        <!-- Related Papers -->
        <div v-if="loadingRelated" class="mt-4 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-7 text-center">
          <div class="flex flex-col items-center gap-3 py-4">
            <div class="h-7 w-7 animate-spin rounded-full border-3 border-[var(--color-primary)] border-t-transparent"></div>
            <span class="text-[13px] text-[var(--color-text-muted)]">Mencari paper terkait dengan AI...</span>
          </div>
        </div>
        <div v-else-if="relatedPapers.length" class="mt-4 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-7">
          <h2 class="text-[15px] font-bold text-[var(--color-text)] mb-4">Paper Terkait ({{ relatedPapers.length }})</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div v-for="rp in relatedPapers" :key="rp.id || rp.external_id"
              @click="router.push(`/papers/${rp.id}`)"
              class="cursor-pointer rounded-xl border border-[var(--color-border)] bg-[var(--color-bg)] p-4 transition hover:border-[var(--color-primary)]">
              <div class="text-[13px] font-semibold leading-snug text-[var(--color-text)] line-clamp-2">{{ rp.title }}</div>
              <div class="mt-1.5 text-[11.5px] text-[var(--color-text-muted)]">
                {{ (rp.authors || []).slice(0, 2).join(', ') }} {{ rp.year ? `· ${rp.year}` : '' }}
              </div>
              <div v-if="rp.citation_count" class="mt-1 text-[11px] text-[var(--color-text-muted)]">📎 {{ rp.citation_count.toLocaleString() }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: AI Panel (sticky) -->
      <div class="lg:sticky lg:top-6">
        <!-- Summarize CTA -->
        <div v-if="!summaryOpen" class="rounded-2xl border border-[var(--color-border)] bg-gradient-to-br from-[var(--color-primary-soft)] to-purple-50 p-6 text-center">
          <div class="text-4xl mb-3">🤖</div>
          <h3 class="text-[15px] font-bold text-[var(--color-text)]">AI Paper Summarizer</h3>
          <p class="mt-1.5 text-[13px] text-[var(--color-text-sub)] leading-relaxed">
            Dapatkan ringkasan paper ini dalam bahasa Indonesia yang mudah dipahami.
          </p>
          <button @click="handleSummarize"
            class="mt-4 w-full rounded-xl bg-[var(--color-primary)] py-2.5 text-[13px] font-semibold text-white transition hover:bg-[var(--color-primary-hover)]">
            ✨ Generate Summary
          </button>
        </div>

        <!-- Summary Result -->
        <div v-else class="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] overflow-hidden">
          <div class="bg-gradient-to-r from-[var(--color-primary-soft)] to-purple-50 px-5 py-4 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-[var(--color-primary)]">✨</span>
              <span class="text-[14px] font-bold text-[var(--color-text)]">AI Summary</span>
              <span class="rounded-full bg-[var(--color-primary)] px-2 py-0.5 text-[10px] font-bold text-white">Groq</span>
            </div>
            <button @click="summaryOpen = false" class="text-[var(--color-text-muted)] hover:text-[var(--color-text)] text-lg">×</button>
          </div>

          <div class="p-5">
            <!-- Loading -->
            <div v-if="aiStore.loading" class="flex flex-col items-center gap-3 py-8">
              <div class="h-7 w-7 animate-spin rounded-full border-3 border-[var(--color-primary)] border-t-transparent"></div>
              <span class="text-[12px] text-[var(--color-text-muted)]">Generating summary...</span>
            </div>

            <!-- Result -->
            <div v-else-if="summaryData">
              <div class="mb-4">
                <div class="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-muted)] mb-2">Ringkasan</div>
                <p class="text-[13px] leading-[1.7] text-[var(--color-text)]">{{ summaryData.ringkasan || 'Ringkasan tidak tersedia.' }}</p>
              </div>

              <div v-if="summaryData.temuan.length" class="mb-4">
                <div class="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-muted)] mb-2">Temuan Utama</div>
                <div v-for="(f, i) in summaryData.temuan" :key="i" class="flex gap-2 items-start mb-1.5">
                  <span class="text-green-500 text-[12px] mt-0.5">✓</span>
                  <span class="text-[12.5px] text-[var(--color-text)]">{{ f }}</span>
                </div>
              </div>

              <div v-if="summaryData.metodologi" class="rounded-xl bg-amber-50 border border-amber-200 p-3.5">
                <div class="text-[10px] font-bold uppercase tracking-wider text-amber-600 mb-1.5">Metodologi</div>
                <p class="text-[12.5px] leading-[1.6] text-[var(--color-text)]">{{ summaryData.metodologi }}</p>
              </div>

              <button @click="handleSummarize"
                class="mt-4 w-full rounded-xl border border-[var(--color-border)] py-2 text-[12px] font-medium text-[var(--color-text-sub)] hover:bg-gray-50 transition">
                Regenerate Summary
              </button>
            </div>
          </div>
        </div>

        <!-- Explain Text -->
        <div class="mt-4 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
          <h3 class="text-[14px] font-bold text-[var(--color-text)] mb-3 flex items-center gap-2">💬 Jelaskan Teks</h3>
          <textarea v-model="explainText"
            placeholder="Paste bagian paper yang ingin dijelaskan..."
            rows="3"
            class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-bg)] px-3.5 py-2.5 text-[13px] outline-none resize-none transition focus:border-[var(--color-primary)]"
          ></textarea>
          <div class="mt-2.5 flex gap-2">
            <button @click="handleExplain" :disabled="!explainText.trim() || explainLoading"
              class="rounded-lg bg-[var(--color-primary)] px-3.5 py-1.5 text-[12px] font-semibold text-white transition hover:bg-[var(--color-primary-hover)] disabled:opacity-50">
              {{ explainLoading ? 'Menjelaskan...' : 'Jelaskan (ID)' }}
            </button>
          </div>
          <!-- Explain Result -->
          <div v-if="explainResult" class="mt-3 rounded-xl bg-blue-50 border border-blue-200 p-3.5">
            <div class="text-[10px] font-bold uppercase tracking-wider text-blue-600 mb-1.5">Penjelasan</div>
            <p class="text-[12.5px] leading-[1.6] text-[var(--color-text)] whitespace-pre-line">{{ explainResult }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
