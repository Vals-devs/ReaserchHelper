<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth = useAuthStore()

// Stats state
const statsData = ref({
  saved_papers: 0,
  collections: 0,
  ai_summaries: 0
})
const loadingStats = ref(true)

// History state
const recentSearches = ref<any[]>([])
const loadingHistory = ref(true)

async function fetchStats() {
  loadingStats.value = true
  try {
    const { data } = await api.get('/dashboard/stats')
    statsData.value = data
  } catch (err) {
    console.error('Failed to fetch dashboard stats:', err)
  } finally {
    loadingStats.value = false
  }
}

async function fetchHistory() {
  loadingHistory.value = true
  try {
    const { data } = await api.get('/history/')
    recentSearches.value = data.slice(0, 3) // Ambil 3 pencarian terbaru
  } catch (err) {
    console.error('Failed to fetch search history:', err)
  } finally {
    loadingHistory.value = false
  }
}

onMounted(() => {
  fetchStats()
  fetchHistory()
})
</script>

<template>
  <div class="px-6 py-5">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-[var(--color-text)]">
          Selamat Datang, {{ auth.user?.name || 'Researcher' }}!
        </h1>
        <p class="mt-1 text-xs text-[var(--color-text-sub)]">
          Temukan, pahami, dan kelola paper ilmiah dengan bantuan AI.
        </p>
      </div>
      
      <!-- Quick Info Badge -->
      <div v-if="auth.user?.institution" class="rounded-full bg-[var(--color-primary-soft)] px-3 py-1 text-xs font-medium text-[var(--color-primary)] border border-blue-100 flex items-center gap-1.5">
        <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 21V10m0 0a3 3 0 10-3-3m3 3a3 3 0 113-3m-9 6.5h12M4.5 19.5h15"/></svg>
        {{ auth.user.institution }}
      </div>
    </div>

    <!-- Dynamic Stats -->
    <div class="mt-6 grid grid-cols-3 gap-3">
      <!-- Saved Papers Card -->
      <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 transition hover:border-zinc-300">
        <div class="mb-2.5 flex items-center justify-between">
          <div class="flex h-8 w-8 items-center justify-center rounded-md bg-[var(--color-primary-soft)] text-[var(--color-primary)]">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          </div>
          <span class="text-[10px] font-medium text-[var(--color-text-muted)]">Real-time</span>
        </div>
        <div v-if="loadingStats" class="h-8 w-16 animate-pulse rounded bg-zinc-100 mb-1"></div>
        <div v-else class="text-2xl font-semibold tracking-tight text-[var(--color-text)]">{{ statsData.saved_papers }}</div>
        <div class="mt-0.5 text-xs text-[var(--color-text-sub)]">Saved Papers</div>
      </div>

      <!-- Collections Card -->
      <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 transition hover:border-zinc-300">
        <div class="mb-2.5 flex items-center justify-between">
          <div class="flex h-8 w-8 items-center justify-center rounded-md bg-amber-50 text-amber-600">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>
          </div>
          <span class="text-[10px] font-medium text-[var(--color-text-muted)]">Real-time</span>
        </div>
        <div v-if="loadingStats" class="h-8 w-16 animate-pulse rounded bg-zinc-100 mb-1"></div>
        <div v-else class="text-2xl font-semibold tracking-tight text-[var(--color-text)]">{{ statsData.collections }}</div>
        <div class="mt-0.5 text-xs text-[var(--color-text-sub)]">Collections</div>
      </div>

      <!-- AI Summaries Card -->
      <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 transition hover:border-zinc-300">
        <div class="mb-2.5 flex items-center justify-between">
          <div class="flex h-8 w-8 items-center justify-center rounded-md bg-emerald-50 text-emerald-600">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 3v1m0 16v1m-8-9H3m18 0h-1"/><circle cx="12" cy="12" r="4"/></svg>
          </div>
          <span class="text-[10px] font-medium text-[var(--color-text-muted)]">Real-time</span>
        </div>
        <div v-if="loadingStats" class="h-8 w-16 animate-pulse rounded bg-zinc-100 mb-1"></div>
        <div v-else class="text-2xl font-semibold tracking-tight text-[var(--color-text)]">{{ statsData.ai_summaries }}</div>
        <div class="mt-0.5 text-xs text-[var(--color-text-sub)]">AI Summaries</div>
      </div>
    </div>

    <!-- Quick Actions & Recent Searches -->
    <div class="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Quick Actions -->
      <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4">
        <h3 class="mb-3 text-xs font-bold uppercase tracking-wider text-[var(--color-text-muted)]">Quick Actions</h3>
        <div class="flex flex-col gap-2">
          <router-link to="/search" class="flex items-center gap-3 rounded-md bg-[var(--color-bg)] px-3.5 py-3 border border-[var(--color-border)] transition hover:bg-zinc-50 hover:border-zinc-300">
            <div class="h-2 w-2 rounded-full bg-[var(--color-primary)]"></div>
            <div class="flex-1">
              <div class="text-sm font-semibold text-[var(--color-text)]">Cari Paper Baru</div>
              <div class="text-[11px] text-[var(--color-text-muted)]">Cari ribuan jurnal ilmiah lewat Semantic Scholar & arXiv</div>
            </div>
          </router-link>
          
          <router-link to="/gap-analysis" class="flex items-center gap-3 rounded-md bg-[var(--color-bg)] px-3.5 py-3 border border-[var(--color-border)] transition hover:bg-zinc-50 hover:border-zinc-300">
            <div class="h-2 w-2 rounded-full bg-violet-500"></div>
            <div class="flex-1">
              <div class="text-sm font-semibold text-[var(--color-text)]">Analisis Research Gap</div>
              <div class="text-[11px] text-[var(--color-text-muted)]">Temukan celah penelitian baru secara mendalam dari kumpulan paper</div>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Recent Searches -->
      <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 flex flex-col justify-between">
        <div>
          <h3 class="mb-3 text-xs font-bold uppercase tracking-wider text-[var(--color-text-muted)]">Recent Searches</h3>
          
          <div v-if="loadingHistory" class="space-y-2.5">
            <div v-for="i in 3" :key="i" class="h-9 w-full animate-pulse rounded bg-zinc-50 border border-zinc-100"></div>
          </div>
          
          <div v-else-if="recentSearches.length > 0" class="flex flex-col gap-1.5">
            <div v-for="q in recentSearches" :key="q.id" class="flex items-center gap-2.5 rounded-md bg-[var(--color-bg)] px-3 py-2 border border-[var(--color-border)]">
              <svg width="14" height="14" class="flex-shrink-0 text-[var(--color-text-muted)]" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>
              <span class="flex-1 truncate text-xs font-medium text-[var(--color-text)]">{{ q.query }}</span>
              <span v-if="q.result_count !== undefined" class="text-[10px] text-[var(--color-text-muted)]">{{ q.result_count }} hasil</span>
            </div>
          </div>

          <div v-else class="text-center py-6 text-xs text-[var(--color-text-muted)]">
            <svg width="24" height="24" class="mx-auto text-zinc-300 mb-1.5" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>
            Belum ada riwayat pencarian.
          </div>
        </div>

        <router-link to="/history" v-if="recentSearches.length > 0" class="mt-3 text-right text-xs font-medium text-[var(--color-primary)] hover:underline">
          Lihat Semua Riwayat →
        </router-link>
      </div>
    </div>
  </div>
</template>
