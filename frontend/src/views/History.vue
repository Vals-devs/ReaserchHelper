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
  <div class="p-7 max-w-3xl">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-xl font-extrabold text-[var(--color-text)]">Riwayat Pencarian</h1>
        <p class="mt-1 text-[13px] text-[var(--color-text-sub)]">{{ history.length }} pencarian tersimpan</p>
      </div>
      <button v-if="history.length" @click="clearAll"
        class="rounded-xl border border-red-200 bg-red-50 px-4 py-2 text-[13px] font-medium text-red-600 transition hover:bg-red-100">
        🗑 Hapus Semua
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="h-8 w-8 animate-spin rounded-full border-3 border-[var(--color-primary)] border-t-transparent"></div>
    </div>

    <!-- History List -->
    <div v-else-if="history.length" class="flex flex-col gap-2.5">
      <div v-for="item in history" :key="item.id"
        class="flex items-center gap-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] px-5 py-4 transition hover:border-[var(--color-primary)]">
        <div class="flex-1 min-w-0">
          <button @click="reSearch(item)" class="text-left">
            <div class="text-[14px] font-semibold text-[var(--color-text)] hover:text-[var(--color-primary)] transition">
              "{{ item.query }}"
            </div>
          </button>
          <div class="mt-1 flex items-center gap-3 text-[12px] text-[var(--color-text-muted)]">
            <span>📊 {{ item.result_count }} hasil</span>
            <span v-if="item.filters?.source && item.filters.source !== 'all'" class="rounded-full bg-[var(--color-primary-soft)] px-2 py-0.5 text-[10px] font-medium text-[var(--color-primary)]">
              {{ item.filters.source }}
            </span>
            <span>{{ formatDate(item.searched_at) }}</span>
          </div>
        </div>
        <div class="flex gap-2 flex-shrink-0">
          <button @click="reSearch(item)"
            class="rounded-lg bg-[var(--color-primary-soft)] px-3 py-1.5 text-[11.5px] font-semibold text-[var(--color-primary)] transition hover:bg-blue-100">
            Cari Lagi
          </button>
          <button @click="deleteItem(item.id)"
            class="rounded-lg border border-[var(--color-border)] px-2.5 py-1.5 text-[11.5px] text-red-500 transition hover:bg-red-50">
            🗑
          </button>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] py-16 text-center">
      <div class="text-5xl">🕐</div>
      <h3 class="mt-3 text-base font-semibold">Belum ada riwayat</h3>
      <p class="mt-1 text-[13px] text-[var(--color-text-sub)]">Mulai cari paper dan riwayatmu akan muncul di sini.</p>
      <router-link to="/search"
        class="mt-4 inline-block rounded-xl bg-[var(--color-primary)] px-5 py-2 text-[13px] font-semibold text-white transition hover:bg-[var(--color-primary-hover)]">
        Mulai Cari
      </router-link>
    </div>
  </div>
</template>
