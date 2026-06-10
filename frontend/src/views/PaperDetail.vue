<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const paperId = route.params.id
</script>

<template>
  <div class="p-7">
    <router-link to="/search" class="mb-5 inline-flex items-center gap-1.5 text-[13px] text-[var(--color-text-sub)] hover:text-[var(--color-primary)]">
      ← Kembali ke hasil pencarian
    </router-link>
    <div class="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-7">
      <h1 class="text-xl font-bold text-[var(--color-text)]">Paper Detail</h1>
      <p class="mt-1 text-[13px] text-[var(--color-text-muted)]">Paper ID: {{ paperId }}</p>
      <p class="mt-4 text-[13px] text-[var(--color-text-sub)]">Paper detail will be loaded here.</p>
    </div>
  </div>
</template>
