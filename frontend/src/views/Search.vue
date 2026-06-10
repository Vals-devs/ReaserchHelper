<script setup lang="ts">
import { ref } from 'vue'
import { usePapersStore } from '@/stores/papers'

const papersStore = usePapersStore()
const searchQuery = ref('')

function handleSearch() {
  if (searchQuery.value.trim()) {
    papersStore.search(searchQuery.value)
  }
}
</script>

<template>
  <div class="p-7">
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
      <button @click="handleSearch" class="rounded-xl bg-[var(--color-primary)] px-5 py-2 text-[13px] font-semibold text-white transition hover:bg-[var(--color-primary-hover)]">
        Cari
      </button>
    </div>

    <!-- Loading -->
    <div v-if="papersStore.loading" class="mt-10 text-center text-[var(--color-text-muted)]">
      Loading...
    </div>

    <!-- Results -->
    <div v-else-if="papersStore.results.length" class="mt-5">
      <p class="mb-3 text-[13px] text-[var(--color-text-sub)]">
        Menampilkan <strong>{{ papersStore.results.length }}</strong> hasil untuk "{{ papersStore.query }}"
      </p>
      <div class="flex flex-col gap-3.5">
        <div v-for="paper in papersStore.results" :key="paper.id" class="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
          <h3 class="text-[15px] font-bold text-[var(--color-text)]">{{ paper.title }}</h3>
          <p class="mt-1 text-[12.5px] text-[var(--color-text-sub)]">{{ paper.authors.join(', ') }}</p>
          <p v-if="paper.abstract" class="mt-2 line-clamp-3 text-[13px] text-[var(--color-text-sub)]">{{ paper.abstract }}</p>
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
