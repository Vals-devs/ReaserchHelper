<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const collectionId = route.params.id
</script>

<template>
  <div class="p-7">
    <router-link to="/collections" class="mb-5 inline-flex items-center gap-1.5 text-[13px] text-[var(--color-text-sub)]">
      ← Semua Collections
    </router-link>
    <div class="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-7">
      <h1 class="text-xl font-bold text-[var(--color-text)]">Collection Detail</h1>
      <p class="mt-1 text-[13px] text-[var(--color-text-muted)]">Collection ID: {{ collectionId }}</p>
    </div>
  </div>
</template>
