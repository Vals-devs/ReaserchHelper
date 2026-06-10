<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const stats = [
  { label: 'Saved Papers', value: '47', change: '+5 this week', color: 'var(--color-primary)', bg: 'var(--color-primary-soft)' },
  { label: 'Collections', value: '12', change: '+2 this week', color: 'var(--color-warning)', bg: '#FEF7E0' },
  { label: 'AI Summaries', value: '23', change: '+3 this week', color: 'var(--color-success)', bg: '#E6F4EA' },
]
</script>

<template>
  <div class="p-7">
    <h1 class="text-2xl font-extrabold tracking-tight text-[var(--color-text)]">
      Selamat Datang, {{ auth.user?.name || 'Researcher' }}!
    </h1>
    <p class="mt-1.5 text-sm text-[var(--color-text-sub)]">
      Temukan, pahami, dan kelola paper ilmiah dengan bantuan AI.
    </p>

    <!-- Stats -->
    <div class="mt-7 grid grid-cols-3 gap-4">
      <div v-for="s in stats" :key="s.label" class="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
        <div class="mb-3 flex items-center justify-between">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl" :style="{ background: s.bg, color: s.color }">
            <div class="h-2.5 w-2.5 rounded-full" :style="{ background: s.color }"></div>
          </div>
          <span class="text-xs font-semibold text-[var(--color-success)]">{{ s.change }}</span>
        </div>
        <div class="text-[30px] font-extrabold tracking-tight text-[var(--color-text)]">{{ s.value }}</div>
        <div class="mt-0.5 text-[13px] font-medium text-[var(--color-text-sub)]">{{ s.label }}</div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="mt-7 grid grid-cols-2 gap-4">
      <div class="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
        <h3 class="mb-4 text-sm font-bold text-[var(--color-text)]">Quick Actions</h3>
        <div class="flex flex-col gap-2">
          <router-link to="/search" class="flex items-center gap-3 rounded-xl bg-[var(--color-bg)] px-3.5 py-3 transition hover:border-[var(--color-border)]">
            <div class="h-2 w-2 rounded-full bg-[var(--color-primary)]"></div>
            <div class="flex-1">
              <div class="text-[13px] font-semibold text-[var(--color-text)]">Cari Paper Baru</div>
              <div class="text-[11.5px] text-[var(--color-text-muted)]">Semantic Scholar + arXiv</div>
            </div>
          </router-link>
          <router-link to="/gap-analysis" class="flex items-center gap-3 rounded-xl bg-[var(--color-bg)] px-3.5 py-3 transition">
            <div class="h-2 w-2 rounded-full bg-purple-600"></div>
            <div class="flex-1">
              <div class="text-[13px] font-semibold text-[var(--color-text)]">Analisis Research Gap</div>
              <div class="text-[11.5px] text-[var(--color-text-muted)]">Temukan celah penelitian</div>
            </div>
          </router-link>
        </div>
      </div>
      <div class="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
        <h3 class="mb-4 text-sm font-bold text-[var(--color-text)]">Recent Searches</h3>
        <div class="flex flex-col gap-1.5">
          <div v-for="q in ['transformer neural network', 'BERT fine-tuning', 'attention mechanism']" :key="q" class="flex items-center gap-3 rounded-xl bg-[var(--color-bg)] px-3.5 py-2.5">
            <span class="text-[var(--color-text-muted)]">🔍</span>
            <span class="flex-1 truncate text-[13px] text-[var(--color-text)]">{{ q }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
