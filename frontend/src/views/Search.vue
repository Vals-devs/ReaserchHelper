<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePapersStore } from '@/stores/papers'

const papersStore = usePapersStore()
const router = useRouter()
const route = useRoute()
const searchQuery = ref('')
const selectedSource = ref('all')
const selectedField = ref('')

// Auto-search from URL query param (e.g. from history "Cari Lagi")
onMounted(() => {
  const q = route.query.q as string
  if (q) {
    searchQuery.value = q
    handleSearch()
  }
})

const sourceOptions = [
  { value: 'all', label: 'Semua Sumber' },
  { value: 'semantic_scholar', label: 'Semantic Scholar' },
  { value: 'arxiv', label: 'arXiv' },
]

const fieldOptions = [
  { value: '', label: 'Semua Bidang' },
  { value: 'Computer Science', label: 'Computer Science' },
  { value: 'Medicine', label: 'Medicine' },
  { value: 'Engineering', label: 'Engineering' },
  { value: 'Physics', label: 'Physics' },
  { value: 'Mathematics', label: 'Mathematics' },
  { value: 'Biology', label: 'Biology' },
]

function handleSearch() {
  if (!searchQuery.value.trim()) return
  const filters: Record<string, string> = {}
  if (selectedSource.value !== 'all') filters.source = selectedSource.value
  if (selectedField.value) filters.field = selectedField.value
  papersStore.search(searchQuery.value, filters)
}

function openPaper(paperId: string) {
  router.push(`/papers/${paperId}`)
}

function formatAuthors(authors: string[]): string {
  if (!authors?.length) return 'Unknown authors'
  if (authors.length <= 3) return authors.join(', ')
  return `${authors.slice(0, 3).join(', ')} et al.`
}
</script>

<template>
  <div class="p-7 max-w-4xl">
    <h1 class="text-xl font-extrabold text-[var(--color-text)]">Search Papers</h1>
    <p class="mt-1 text-[13px] text-[var(--color-text-sub)]">Cari dari Semantic Scholar dan arXiv secara bersamaan</p>

    <!-- Search Bar -->
    <div class="mt-5 flex items-center gap-3 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] px-5 py-3.5 shadow-sm">
      <span class="text-[var(--color-text-muted)]">🔍</span>
      <input
        v-model="searchQuery"
        @keyup.enter="handleSearch"
        type="text"
        placeholder="Cari paper berdasarkan judul, keyword, atau topik..."
        class="flex-1 bg-transparent text-[15px] text-[var(--color-text)] outline-none placeholder:text-[var(--color-text-muted)]"
      />
      <button @click="handleSearch" :disabled="papersStore.loading"
        class="rounded-xl bg-[var(--color-primary)] px-5 py-2 text-[13px] font-semibold text-white transition hover:bg-[var(--color-primary-hover)] disabled:opacity-50">
        {{ papersStore.loading ? 'Mencari...' : 'Cari' }}
      </button>
    </div>

    <!-- Filters -->
    <div class="mt-3 flex flex-wrap items-center gap-2">
      <button v-for="opt in sourceOptions" :key="opt.value"
        @click="selectedSource = opt.value"
        class="rounded-full px-3.5 py-1.5 text-[12px] font-medium transition"
        :class="selectedSource === opt.value
          ? 'bg-[var(--color-primary-soft)] text-[var(--color-primary)]'
          : 'bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-sub)] hover:bg-gray-50'">
        {{ opt.label }}
      </button>
      <select v-model="selectedField"
        class="rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-1.5 text-[12px] text-[var(--color-text-sub)] outline-none">
        <option v-for="opt in fieldOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>
    </div>

    <!-- Error -->
    <div v-if="papersStore.error" class="mt-4 rounded-lg bg-red-50 border border-red-200 px-3.5 py-2.5 text-[13px] text-red-700">
      {{ papersStore.error }}
    </div>

    <!-- Loading -->
    <div v-if="papersStore.loading" class="mt-10 flex flex-col items-center gap-3">
      <div class="h-8 w-8 animate-spin rounded-full border-3 border-[var(--color-primary)] border-t-transparent"></div>
      <span class="text-[13px] text-[var(--color-text-muted)]">Mencari di Semantic Scholar dan arXiv...</span>
    </div>

    <!-- Results -->
    <div v-else-if="papersStore.results.length" class="mt-5">
      <!-- Summary -->
      <div class="mb-4 flex items-center justify-between">
        <p class="text-[13px] text-[var(--color-text-sub)]">
          <strong class="text-[var(--color-text)]">{{ papersStore.total }}</strong> hasil untuk
          "<strong class="text-[var(--color-text)]">{{ papersStore.query }}</strong>"
        </p>
        <div class="flex items-center gap-2 text-[11.5px] text-[var(--color-text-muted)]">
          <span v-if="papersStore.sources.semantic_scholar" class="rounded-full bg-[var(--color-primary-soft)] px-2 py-0.5 font-medium text-[var(--color-primary)]">
            S2: {{ papersStore.sources.semantic_scholar }}
          </span>
          <span v-if="papersStore.sources.arxiv" class="rounded-full bg-purple-50 px-2 py-0.5 font-medium text-purple-600">
            arXiv: {{ papersStore.sources.arxiv }}
          </span>
        </div>
      </div>

      <!-- Warnings -->
      <div v-if="papersStore.errors.length" class="mb-3 rounded-lg bg-yellow-50 border border-yellow-200 px-3 py-2 text-[12px] text-yellow-700">
        <div v-for="(err, i) in papersStore.errors" :key="i">{{ err }}</div>
      </div>

      <!-- Paper Cards -->
      <div class="flex flex-col gap-3">
        <div v-for="paper in papersStore.results" :key="paper.id"
          @click="openPaper(paper.id)"
          class="cursor-pointer rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5 transition hover:border-[var(--color-primary)] hover:shadow-sm">
          <!-- Header -->
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0 flex-1">
              <div class="mb-1.5 flex flex-wrap items-center gap-1.5">
                <!-- Source badge -->
                <span class="rounded-full px-2 py-0.5 text-[10px] font-semibold"
                  :class="paper.source === 'arxiv'
                    ? 'bg-purple-50 text-purple-600'
                    : paper.source === 'uploaded'
                      ? 'bg-green-50 text-green-600'
                      : 'bg-[var(--color-primary-soft)] text-[var(--color-primary)]'">
                  {{ paper.source === 'semantic_scholar' ? 'Semantic Scholar' : paper.source === 'arxiv' ? 'arXiv' : 'Uploaded' }}
                </span>
                <span v-if="paper.year" class="text-[11px] text-[var(--color-text-muted)]">{{ paper.year }}</span>
                <!-- Field tags -->
                <span v-for="field in (paper.fields_of_study || []).slice(0, 2)" :key="field"
                  class="rounded-md bg-green-50 px-1.5 py-0.5 text-[10px] font-medium text-green-600">
                  {{ field }}
                </span>
              </div>
              <h3 class="text-[14.5px] font-bold leading-snug text-[var(--color-text)]">{{ paper.title }}</h3>
            </div>
            <!-- Citation count -->
            <div v-if="paper.citation_count" class="flex flex-shrink-0 items-center gap-1 rounded-lg bg-[var(--color-bg)] px-2.5 py-1.5 text-[11.5px] text-[var(--color-text-sub)]">
              📎 {{ paper.citation_count.toLocaleString() }}
            </div>
          </div>

          <!-- Authors -->
          <p class="mt-1.5 text-[12.5px] text-[var(--color-text-sub)]">{{ formatAuthors(paper.authors) }}</p>

          <!-- Abstract -->
          <p v-if="paper.abstract" class="mt-2 line-clamp-3 text-[13px] leading-relaxed text-[var(--color-text-sub)]">{{ paper.abstract }}</p>

          <!-- Actions -->
          <div class="mt-3 flex items-center gap-2 border-t border-[var(--color-border)] pt-3">
            <button @click.stop="openPaper(paper.id)"
              class="rounded-lg bg-[var(--color-primary-soft)] px-3 py-1.5 text-[11.5px] font-semibold text-[var(--color-primary)] transition hover:bg-blue-100">
              Detail
            </button>
            <a v-if="paper.url" :href="paper.url" target="_blank" @click.stop
              class="rounded-lg border border-[var(--color-border)] px-3 py-1.5 text-[11.5px] font-medium text-[var(--color-text-sub)] transition hover:bg-gray-50">
              Buka Paper ↗
            </a>
            <button @click.stop
              class="rounded-lg border border-[var(--color-border)] px-3 py-1.5 text-[11.5px] font-medium text-[var(--color-text-sub)] transition hover:bg-gray-50">
              Simpan
            </button>
            <button @click.stop
              class="rounded-lg border border-[var(--color-border)] px-3 py-1.5 text-[11.5px] font-medium text-[var(--color-text-sub)] transition hover:bg-gray-50">
              Summarize
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="mt-12 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] py-16 text-center">
      <div class="text-5xl">📄</div>
      <h3 class="mt-3 text-base font-semibold text-[var(--color-text)]">Mulai pencarian paper ilmiah</h3>
      <p class="mt-1.5 text-[13px] text-[var(--color-text-sub)]">Ketik topik atau keyword untuk menemukan paper dari Semantic Scholar dan arXiv</p>
    </div>
  </div>
</template>
