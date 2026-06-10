<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

interface HistoryItem {
  id: string
  query: string
  filters: Record<string, any>
  result_count: number
  searched_at: string
}

const history = ref<HistoryItem[]>([])
const loading = ref(true)

onMounted(async () => {
  await fetchHistory()
})

async function fetchHistory() {
  loading.value = true
  try {
    const { data } = await api.get('/history/')
    history.value = data
  } catch {
    history.value = []
  } finally {
    loading.value = false
  }
}

function reSearch(item: HistoryItem) {
  router.push({ path: '/search', query: { q: item.query } })
}

async function deleteItem(id: string) {
  try {
    await api.delete(`/history/${id}`)
    history.value = history.value.filter((h) => h.id !== id)
  } catch { /* ignore */ }
}

async function clearAll() {
  try {
    await api.delete('/history/')
    history.value = []
  } catch { /* ignore */ }
}

function formatDate(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="px-6 py-5 w-full">
    <div class="flex items-center justify-between mb-5">
      <div>
        <h1 class="text-lg font-semibold text-[var(--color-text)]">Riwayat Pencarian</h1>
        <p class="mt-0.5 text-sm text-[var(--color-text-sub)]">{{ history.length }} pencarian tersimpan</p>
      </div>
      <button v-if="history.length" @click="clearAll"
        class="rounded-md border border-red-200 bg-red-50 px-3 py-1.5 text-sm font-medium text-red-600 transition hover:bg-red-100">
        <svg width="14" height="14" class="inline mr-1" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6m5 0V4a1 1 0 011-1h2a1 1 0 011 1v2"/></svg>
        Hapus Semua
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-10">
      <div class="h-6 w-6 animate-spin rounded-full border-2 border-[var(--color-primary)] border-t-transparent"></div>
    </div>

    <!-- History List -->
    <div v-else-if="history.length" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4">
      <div v-for="item in history" :key="item.id"
        class="flex items-center gap-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-3 transition hover:border-zinc-300">
        <div class="flex-1 min-w-0">
          <button @click="reSearch(item)" class="text-left">
            <div class="text-sm font-medium text-[var(--color-text)] hover:text-[var(--color-primary)] transition">
              "{{ item.query }}"
            </div>
          </button>
          <div class="mt-0.5 flex items-center gap-2 text-xs text-[var(--color-text-muted)]">
            <span class="flex items-center gap-1">
              <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>
              {{ item.result_count }} hasil
            </span>
            <span v-if="item.filters?.source && item.filters.source !== 'all'" class="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] font-medium text-blue-600">
              {{ item.filters.source }}
            </span>
            <span>{{ formatDate(item.searched_at) }}</span>
          </div>
        </div>
        <div class="flex gap-1.5 flex-shrink-0">
          <button @click="reSearch(item)"
            class="rounded-md bg-[var(--color-primary-soft)] px-2.5 py-1 text-xs font-medium text-[var(--color-primary)] transition hover:bg-blue-100">
            Cari Lagi
          </button>
          <button @click="deleteItem(item.id)"
            class="rounded-md border border-[var(--color-border)] px-2 py-1 text-xs text-red-500 transition hover:bg-red-50">
            <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6m5 0V4a1 1 0 011-1h2a1 1 0 011 1v2"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] py-12 text-center">
      <svg width="40" height="40" class="mx-auto text-[var(--color-text-muted)]" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
      <h3 class="mt-3 text-sm font-medium text-[var(--color-text)]">Belum ada riwayat</h3>
      <p class="mt-1 text-sm text-[var(--color-text-sub)]">Mulai cari paper dan riwayatmu akan muncul di sini.</p>
      <router-link to="/search"
        class="mt-3 inline-block rounded-md bg-[var(--color-primary)] px-4 py-1.5 text-sm font-medium text-white transition hover:bg-[var(--color-primary-hover)]">
        Mulai Cari
      </router-link>
    </div>
  </div>
</template>
