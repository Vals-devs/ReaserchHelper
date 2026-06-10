<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useCollectionsStore } from '@/stores/collections'
import { useRouter } from 'vue-router'

const store = useCollectionsStore()
const router = useRouter()

const showCreateDialog = ref(false)
const newName = ref('')
const newDesc = ref('')
const creating = ref(false)

onMounted(() => store.fetchCollections())

async function handleCreate() {
  if (!newName.value.trim()) return
  creating.value = true
  try {
    await store.createCollection(newName.value, newDesc.value || undefined)
    showCreateDialog.value = false
    newName.value = ''
    newDesc.value = ''
  } catch (err: any) {
    console.error('Failed to create collection:', err)
  } finally {
    creating.value = false
  }
}

async function handleDelete(id: string) {
  if (!confirm('Hapus koleksi ini?')) return
  await store.deleteCollection(id)
}

// Sidebar computed stats
const totalPapers = computed(() => {
  return store.collections.reduce((sum, c) => sum + (c.paper_count || 0), 0)
})

const readyCollections = computed(() => {
  return store.collections.filter(c => c.paper_count >= 3)
})

function navigateToGapAnalysis() {
  router.push('/gap-analysis')
}
</script>

<template>
  <div class="px-6 py-5 w-full">
    <!-- Header -->
    <div class="mb-5 flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-[var(--color-text)]">Collections</h1>
        <p class="mt-0.5 text-xs text-[var(--color-text-sub)]">Kelola koleksi paper ilmiah Anda untuk mempermudah riset akademik.</p>
      </div>
      <button @click="showCreateDialog = !showCreateDialog"
        class="rounded-md bg-[var(--color-primary)] px-3.5 py-2 text-xs font-medium text-white transition hover:bg-[var(--color-primary-hover)]">
        + Koleksi Baru
      </button>
    </div>

    <!-- Two-Column Layout -->
    <div class="grid grid-cols-1 xl:grid-cols-[1fr_320px] gap-5 items-start">
      <!-- Left side: Collections Grid -->
      <div>
        <!-- Create Dialog -->
        <div v-if="showCreateDialog" class="mb-4 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4">
          <h3 class="text-xs font-bold uppercase tracking-wider text-[var(--color-text)] mb-3">Buat Koleksi Baru</h3>
          <div class="flex flex-col gap-2.5">
            <input v-model="newName" type="text" placeholder="Nama koleksi..."
              class="rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-xs outline-none focus:border-[var(--color-primary)]"
              @keyup.enter="handleCreate" />
            <textarea v-model="newDesc" placeholder="Deskripsi (opsional)..." rows="2"
              class="rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-xs outline-none resize-none focus:border-[var(--color-primary)]"></textarea>
            <div class="flex gap-2">
              <button @click="handleCreate" :disabled="!newName.trim() || creating"
                class="rounded-md bg-[var(--color-primary)] px-3.5 py-1.5 text-xs font-medium text-white disabled:opacity-50 transition hover:bg-[var(--color-primary-hover)]">
                {{ creating ? 'Membuat...' : 'Buat Koleksi' }}
              </button>
              <button @click="showCreateDialog = false"
                class="rounded-md border border-[var(--color-border)] px-3.5 py-1.5 text-xs text-[var(--color-text-sub)] transition hover:bg-zinc-50">
                Batal
              </button>
            </div>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="store.loading" class="flex justify-center py-10">
          <div class="h-6 w-6 animate-spin rounded-full border-2 border-[var(--color-primary)] border-t-transparent"></div>
        </div>

        <!-- Collections Grid -->
        <div v-else-if="store.collections.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3.5">
          <router-link v-for="col in store.collections" :key="col.id" :to="`/collections/${col.id}`"
            class="group rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 transition hover:border-zinc-300 hover:shadow-sm">
            <div class="flex items-start justify-between">
              <div class="flex h-8 w-8 items-center justify-center rounded-md bg-[var(--color-primary-soft)] text-[var(--color-primary)]">
                <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>
              </div>
              <button @click.stop.prevent="handleDelete(col.id)"
                class="opacity-0 group-hover:opacity-100 rounded-md p-1 text-[var(--color-text-muted)] hover:bg-red-50 hover:text-red-500 transition">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6m5 0V4a1 1 0 011-1h2a1 1 0 011 1v2"/></svg>
              </button>
            </div>
            <h3 class="mt-2.5 text-sm font-semibold text-[var(--color-text)]">{{ col.name }}</h3>
            <p class="mt-0.5 text-xs text-[var(--color-text-sub)] line-clamp-2 leading-relaxed h-8">{{ col.description || 'Tidak ada deskripsi' }}</p>
            <div class="mt-2.5 flex items-center gap-3 text-xs text-[var(--color-text-muted)] border-t border-[var(--color-border)] pt-2.5">
              <span class="flex items-center gap-1 font-medium">
                <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                {{ col.paper_count || 0 }} paper
              </span>
              <span>{{ new Date(col.created_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'short' }) }}</span>
            </div>
          </router-link>
        </div>

        <!-- Empty State -->
        <div v-else class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] py-12 text-center">
          <svg width="40" height="40" class="mx-auto text-[var(--color-text-muted)]" fill="none" stroke="currentColor" stroke-width="1" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M4 4.5A2.5 2.5 0 016.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15z"/></svg>
          <h3 class="mt-3 text-sm font-medium text-[var(--color-text)]">Belum ada koleksi</h3>
          <p class="mt-1 text-xs text-[var(--color-text-sub)]">Buat koleksi pertamamu untuk menyimpan paper.</p>
          <button @click="showCreateDialog = true"
            class="mt-3 rounded-md bg-[var(--color-primary)] px-4 py-1.5 text-xs font-medium text-white transition hover:bg-[var(--color-primary-hover)]">
            + Buat Koleksi
          </button>
        </div>
      </div>

      <!-- Right side: Sidebar Panel -->
      <div class="space-y-4">
        <!-- Stats Card -->
        <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4">
          <h3 class="text-xs font-bold uppercase tracking-wider text-[var(--color-text-muted)] mb-3">Ikhtisar Koleksi</h3>
          <div class="grid grid-cols-2 gap-2 text-center">
            <div class="rounded-md bg-[var(--color-bg)] p-3 border border-[var(--color-border)]">
              <div class="text-xl font-bold text-[var(--color-text)]">{{ store.collections.length }}</div>
              <div class="text-[10px] text-[var(--color-text-muted)] mt-0.5">Total Koleksi</div>
            </div>
            <div class="rounded-md bg-[var(--color-bg)] p-3 border border-[var(--color-border)]">
              <div class="text-xl font-bold text-[var(--color-text)]">{{ totalPapers }}</div>
              <div class="text-[10px] text-[var(--color-text-muted)] mt-0.5">Paper Tersimpan</div>
            </div>
          </div>
        </div>

        <!-- Gap Analysis Recommendation -->
        <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4">
          <h3 class="text-xs font-bold uppercase tracking-wider text-[var(--color-text-muted)] mb-2.5">Rekomendasi Riset</h3>
          
          <div v-if="readyCollections.length > 0">
            <div class="rounded-md bg-emerald-50 border border-emerald-100 p-3 text-emerald-900 text-[11px] leading-relaxed">
              <div class="font-semibold flex items-center gap-1.5 mb-1.5 text-xs text-emerald-800">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                Siap Analisis Celah Riset!
              </div>
              Terdapat koleksi dengan minimal 3 paper yang siap dianalisis celahnya dengan AI Mentor:
              <ul class="list-disc pl-3.5 mt-1.5 space-y-1 font-medium">
                <li v-for="c in readyCollections" :key="c.id">
                  {{ c.name }} ({{ c.paper_count }} paper)
                </li>
              </ul>
              <button @click="navigateToGapAnalysis"
                class="mt-3 w-full rounded bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-1.5 text-[10px] transition">
                Mulai Analisis Celah ⚡
              </button>
            </div>
          </div>
          
          <div v-else>
            <p class="text-xs text-[var(--color-text-sub)] leading-relaxed">
              Kumpulkan minimal <strong>3 paper</strong> di dalam satu koleksi untuk mengaktifkan fitur <strong>Research Gap Analysis</strong> menggunakan AI Mentor.
            </p>
            <router-link to="/search" class="mt-2.5 inline-block text-xs font-medium text-[var(--color-primary)] hover:underline">
              Cari paper sekarang →
            </router-link>
          </div>
        </div>

        <!-- Tips Card -->
        <div class="rounded-lg border border-amber-100 bg-amber-50/40 p-4">
          <h3 class="text-xs font-bold uppercase tracking-wider text-amber-800 mb-2 flex items-center gap-1">
            <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4m0-4h.01"/></svg>
            Tips Riset Akademik
          </h3>
          <p class="text-[11px] text-amber-900 leading-relaxed">
            Kelompokkan paper berdasarkan topik bab 2 skripsi Anda (misalnya satu folder untuk "Metode", satu untuk "Keamanan", dst.). Hal ini akan memudahkan AI menganalisis kesamaan dan perbedaannya secara spesifik.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
