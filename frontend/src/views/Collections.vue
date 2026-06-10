<script setup lang="ts">
import { onMounted } from 'vue'
import { useCollectionsStore } from '@/stores/collections'

const store = useCollectionsStore()
onMounted(() => store.fetchCollections())
</script>

<template>
  <div class="p-7">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-xl font-extrabold text-[var(--color-text)]">Collections</h1>
        <p class="mt-1 text-[13px] text-[var(--color-text-sub)]">Kelola koleksi paper ilmiah kamu</p>
      </div>
      <button class="rounded-xl bg-[var(--color-primary)] px-4 py-2 text-[13px] font-semibold text-white">
        + Koleksi Baru
      </button>
    </div>

    <div v-if="store.loading" class="text-center text-[var(--color-text-muted)]">Loading...</div>
    <div v-else-if="store.collections.length" class="grid grid-cols-3 gap-4">
      <router-link
        v-for="col in store.collections"
        :key="col.id"
        :to="`/collections/${col.id}`"
        class="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5 transition hover:border-[var(--color-primary)]"
      >
        <h3 class="text-sm font-bold text-[var(--color-text)]">{{ col.name }}</h3>
        <p class="mt-1 text-[12.5px] text-[var(--color-text-sub)]">{{ col.description || 'No description' }}</p>
      </router-link>
    </div>
    <div v-else class="mt-12 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] py-16 text-center">
      <div class="text-5xl">📚</div>
      <h3 class="mt-3 text-base font-semibold">Belum ada koleksi</h3>
      <p class="mt-1 text-[13px] text-[var(--color-text-sub)]">Buat koleksi pertamamu untuk menyimpan paper.</p>
    </div>
  </div>
</template>
