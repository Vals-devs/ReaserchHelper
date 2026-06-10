<script setup lang="ts">
import { ref, onMounted } from 'vue'
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
  <div class="px-6 py-5 w-full">
    <h1 class="text-lg font-semibold text-[var(--color-text)]">Search Papers</h1>
    <p class="mt-0.5 text-sm text-[var(--color-text-sub)]">Cari dari Semantic Scholar dan arXiv secara bersamaan</p>

    <!-- Search Bar -->
    <div class="mt-4 flex items-center gap-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-2.5">
      <svg width="16" height="16" class="flex-shrink-0 text-[var(--color-text-muted)]" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>
      <input
        v-model="searchQuery"
        @keyup.enter="handleSearch"
        type="text"
        placeholder="Cari paper berdasarkan judul, keyword, atau topik..."
        class="flex-1 bg-transparent text-sm text-[var(--color-text)] outline-none placeholder:text-[var(--color-text-muted)]"
      />
      <button @click="handleSearch" :disabled="papersStore.loading"
        class="rounded-md bg-[var(--color-primary)] px-4 py-1.5 text-sm font-medium text-white transition hover:bg-[var(--color-primary-hover)] disabled:opacity-50">
        {{ papersStore.loading ? 'Mencari...' : 'Cari' }}
      </button>
    </div>

    <!-- Filters -->
    <div class="mt-2.5 flex flex-wrap items-center gap-1.5">
      <button v-for="opt in sourceOptions" :key="opt.value"
        @click="selectedSource = opt.value"
        class="rounded-md px-3 py-1 text-xs font-medium transition"
        :class="selectedSource === opt.value
          ? 'bg-[var(--color-primary-soft)] text-[var(--color-primary)]'
          : 'bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-sub)] hover:bg-zinc-50'">
        {{ opt.label }}
      </button>
      <select v-model="selectedField"
        class="rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-2.5 py-1 text-xs text-[var(--color-text-sub)] outline-none">
        <option v-for="opt in fieldOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>
    </div>

    <!-- Error -->
    <div v-if="papersStore.error" class="mt-3 rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
      {{ papersStore.error }}
    </div>

    <!-- Loading -->
    <div v-if="papersStore.loading" class="mt-8 flex flex-col items-center gap-2.5">
      <div class="h-6 w-6 animate-spin rounded-full border-2 border-[var(--color-primary)] border-t-transparent"></div>
      <span class="text-sm text-[var(--color-text-muted)]">Mencari di Semantic Scholar dan arXiv...</span>
    </div>

    <!-- Results -->
    <div v-else-if="papersStore.results.length" class="mt-4">
      <!-- Summary -->
      <div class="mb-3 flex items-center justify-between">
        <p class="text-sm text-[var(--color-text-sub)]">
          <strong class="font-medium text-[var(--color-text)]">{{ papersStore.total }}</strong> hasil untuk
          "<strong class="font-medium text-[var(--color-text)]">{{ papersStore.query }}</strong>"
        </p>
        <div class="flex items-center gap-1.5 text-xs text-[var(--color-text-muted)]">
          <span v-if="papersStore.sources.semantic_scholar" class="rounded bg-blue-50 px-1.5 py-0.5 font-medium text-blue-600">
            S2: {{ papersStore.sources.semantic_scholar }}
          </span>
          <span v-if="papersStore.sources.arxiv" class="rounded bg-violet-50 px-1.5 py-0.5 font-medium text-violet-600">
            arXiv: {{ papersStore.sources.arxiv }}
          </span>
        </div>
      </div>

      <!-- Warnings -->
      <div v-if="papersStore.errors.length" class="mb-2.5 rounded-md bg-amber-50 border border-amber-200 px-3 py-2 text-xs text-amber-700">
        <div v-for="(err, i) in papersStore.errors" :key="i">{{ err }}</div>
      </div>

      <!-- Paper Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4">
        <div v-for="paper in papersStore.results" :key="paper.id"
          @click="openPaper(paper.id)"
          class="cursor-pointer rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 transition hover:border-zinc-300">
          <!-- Header -->
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0 flex-1">
              <div class="mb-1 flex flex-wrap items-center gap-1.5">
                <!-- Source badge -->
                <span class="rounded px-1.5 py-0.5 text-[10px] font-medium"
                  :class="paper.source === 'arxiv'
                    ? 'bg-violet-50 text-violet-600'
                    : paper.source === 'uploaded'
                      ? 'bg-emerald-50 text-emerald-600'
                      : 'bg-blue-50 text-blue-600'">
                  {{ paper.source === 'semantic_scholar' ? 'Semantic Scholar' : paper.source === 'arxiv' ? 'arXiv' : 'Uploaded' }}
                </span>
                <span v-if="paper.year" class="text-xs text-[var(--color-text-muted)]">{{ paper.year }}</span>
                <!-- Field tags -->
                <span v-for="field in (paper.fields_of_study || []).slice(0, 2)" :key="field"
                  class="rounded bg-emerald-50 px-1.5 py-0.5 text-[10px] font-medium text-emerald-600">
                  {{ field }}
                </span>
              </div>
              <h3 class="text-sm font-medium leading-snug text-[var(--color-text)]">{{ paper.title }}</h3>
            </div>
            <!-- Citation count -->
            <div v-if="paper.citation_count" class="flex flex-shrink-0 items-center gap-1 rounded-md bg-[var(--color-bg)] px-2 py-1 text-xs text-[var(--color-text-sub)]">
              <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M7 17l9.2-9.2M17 17V7H7"/></svg>
              {{ paper.citation_count.toLocaleString() }}
            </div>
          </div>

          <!-- Authors -->
          <p class="mt-1 text-xs text-[var(--color-text-sub)]">{{ formatAuthors(paper.authors) }}</p>

          <!-- Abstract -->
          <p v-if="paper.abstract" class="mt-1.5 line-clamp-3 text-sm leading-relaxed text-[var(--color-text-sub)]">{{ paper.abstract }}</p>

          <!-- Actions -->
          <div class="mt-2.5 flex items-center gap-1.5 border-t border-[var(--color-border)] pt-2.5">
            <button @click.stop="openPaper(paper.id)"
              class="rounded-md bg-[var(--color-primary-soft)] px-2.5 py-1 text-xs font-medium text-[var(--color-primary)] transition hover:bg-blue-100">
              Detail
            </button>
            <a v-if="paper.url" :href="paper.url" target="_blank" @click.stop
              class="rounded-md border border-[var(--color-border)] px-2.5 py-1 text-xs font-medium text-[var(--color-text-sub)] transition hover:bg-zinc-50">
              Buka Paper ↗
            </a>
            <button @click.stop
              class="rounded-md border border-[var(--color-border)] px-2.5 py-1 text-xs font-medium text-[var(--color-text-sub)] transition hover:bg-zinc-50">
              Simpan
            </button>
            <button @click.stop
              class="rounded-md border border-[var(--color-border)] px-2.5 py-1 text-xs font-medium text-[var(--color-text-sub)] transition hover:bg-zinc-50">
              Summarize
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="mt-8 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] py-12 text-center">
      <svg width="40" height="40" class="mx-auto text-[var(--color-text-muted)]" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
      <h3 class="mt-3 text-sm font-medium text-[var(--color-text)]">Mulai pencarian paper ilmiah</h3>
      <p class="mt-1 text-sm text-[var(--color-text-sub)]">Ketik topik atau keyword untuk menemukan paper dari Semantic Scholar dan arXiv</p>
    </div>
  </div>
</template>
