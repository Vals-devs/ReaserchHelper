<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCollectionsStore } from '@/stores/collections'

const store = useCollectionsStore()
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
</script>

<template>
  <div class="p-7 max-w-4xl">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-xl font-extrabold text-[var(--color-text)]">Collections</h1>
        <p class="mt-1 text-[13px] text-[var(--color-text-sub)]">Kelola koleksi paper ilmiah kamu</p>
      </div>
      <button @click="showCreateDialog = !showCreateDialog"
        class="rounded-xl bg-[var(--color-primary)] px-4 py-2.5 text-[13px] font-semibold text-white transition hover:bg-[var(--color-primary-hover)]">
        + Koleksi Baru
      </button>
    </div>

    <!-- Create Dialog -->
    <div v-if="showCreateDialog" class="mb-5 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
      <h3 class="text-[14px] font-bold text-[var(--color-text)] mb-3">Buat Koleksi Baru</h3>
      <div class="flex flex-col gap-3">
        <input v-model="newName" type="text" placeholder="Nama koleksi..."
          class="rounded-xl border border-[var(--color-border)] bg-[var(--color-bg)] px-3.5 py-2.5 text-[13.5px] outline-none focus:border-[var(--color-primary)]"
          @keyup.enter="handleCreate" />
        <textarea v-model="newDesc" placeholder="Deskripsi (opsional)..." rows="2"
          class="rounded-xl border border-[var(--color-border)] bg-[var(--color-bg)] px-3.5 py-2.5 text-[13.5px] outline-none resize-none focus:border-[var(--color-primary)]"></textarea>
        <div class="flex gap-2">
          <button @click="handleCreate" :disabled="!newName.trim() || creating"
            class="rounded-xl bg-[var(--color-primary)] px-4 py-2 text-[13px] font-semibold text-white disabled:opacity-50 transition hover:bg-[var(--color-primary-hover)]">
            {{ creating ? 'Membuat...' : 'Buat Koleksi' }}
          </button>
          <button @click="showCreateDialog = false"
            class="rounded-xl border border-[var(--color-border)] px-4 py-2 text-[13px] text-[var(--color-text-sub)] transition hover:bg-gray-50">
            Batal
          </button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="flex justify-center py-12">
      <div class="h-8 w-8 animate-spin rounded-full border-3 border-[var(--color-primary)] border-t-transparent"></div>
    </div>

    <!-- Collections Grid -->
    <div v-else-if="store.collections.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <router-link v-for="col in store.collections" :key="col.id" :to="`/collections/${col.id}`"
        class="group rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5 transition hover:border-[var(--color-primary)] hover:shadow-sm">
        <div class="flex items-start justify-between">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--color-primary-soft)] text-[var(--color-primary)] text-lg">
            📁
          </div>
          <button @click.prevent="handleDelete(col.id)"
            class="opacity-0 group-hover:opacity-100 rounded-lg p-1.5 text-[var(--color-text-muted)] hover:bg-red-50 hover:text-red-500 transition">
            🗑
          </button>
        </div>
        <h3 class="mt-3 text-[14px] font-bold text-[var(--color-text)]">{{ col.name }}</h3>
        <p class="mt-1 text-[12.5px] text-[var(--color-text-sub)] line-clamp-2">{{ col.description || 'Tidak ada deskripsi' }}</p>
        <div class="mt-3 flex items-center gap-3 text-[11.5px] text-[var(--color-text-muted)] border-t border-[var(--color-border)] pt-3">
          <span>📄 {{ col.paper_count || 0 }} paper</span>
          <span>{{ new Date(col.created_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'short' }) }}</span>
        </div>
      </router-link>
    </div>

    <!-- Empty -->
    <div v-else class="mt-12 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] py-16 text-center">
      <div class="text-5xl">📚</div>
      <h3 class="mt-3 text-base font-semibold">Belum ada koleksi</h3>
      <p class="mt-1 text-[13px] text-[var(--color-text-sub)]">Buat koleksi pertamamu untuk menyimpan paper.</p>
      <button @click="showCreateDialog = true"
        class="mt-4 rounded-xl bg-[var(--color-primary)] px-5 py-2 text-[13px] font-semibold text-white transition hover:bg-[var(--color-primary-hover)]">
        + Buat Koleksi
      </button>
    </div>
  </div>
</template>
