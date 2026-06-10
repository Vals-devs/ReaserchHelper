<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const menuItems = [
  {
    id: 'dashboard', label: 'Dashboard', path: '/dashboard',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/><path d="M9 21V12h6v9"/></svg>`
  },
  {
    id: 'search', label: 'Search Papers', path: '/search',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>`
  },
  {
    id: 'collections', label: 'Collections', path: '/collections',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M4 4.5A2.5 2.5 0 016.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15z"/></svg>`
  },
  {
    id: 'history', label: 'Search History', path: '/history',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>`
  },
  {
    id: 'gap', label: 'Gap Analysis', path: '/gap-analysis',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>`
  },
]

function isActive(path: string) {
  return route.path === path || route.path.startsWith(path + '/')
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <aside class="fixed left-0 top-0 z-20 flex h-screen w-[252px] flex-col border-r border-[var(--color-border)] bg-[var(--color-surface)] py-4">
    <!-- Brand -->
    <router-link to="/dashboard" class="flex items-center gap-2.5 px-5 pb-5">
      <img src="@/assets/logo.png" class="h-11 w-11 object-contain rounded-md" alt="ResearchFinder Logo" />
      <div>
        <div class="text-sm font-semibold text-[var(--color-text)]">ResearchFinder</div>
        <div class="text-xs text-[var(--color-text-muted)]">AI Research Tool</div>
      </div>
    </router-link>

    <!-- New Search CTA -->
    <div class="px-3 mb-1.5">
      <router-link
        to="/search"
        class="flex w-full items-center justify-center gap-2 rounded-md bg-[var(--color-primary)] px-4 py-2 text-sm font-medium text-white transition hover:bg-[var(--color-primary-hover)]"
      >
        <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        New Search
      </router-link>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto px-2.5 py-2">
      <div class="px-2.5 pb-1.5 text-xs font-medium uppercase tracking-wider text-[var(--color-text-muted)]">Navigation</div>
      <router-link
        v-for="item in menuItems"
        :key="item.id"
        :to="item.path"
        class="mb-0.5 flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm transition"
        :class="isActive(item.path) ? 'bg-[var(--color-primary-soft)] font-medium text-[var(--color-primary)]' : 'text-[var(--color-text-sub)] hover:bg-zinc-50'"
      >
        <span class="flex-shrink-0 [&>svg]:h-[18px] [&>svg]:w-[18px]" v-html="item.icon"></span>
        {{ item.label }}
      </router-link>
    </nav>

    <!-- Bottom -->
    <div class="border-t border-[var(--color-border)] px-2.5 pt-2">
      <router-link to="/settings" class="flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm text-[var(--color-text-muted)] hover:bg-zinc-50">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 11-4 0v-.09a1.65 1.65 0 00-1.08-1.51 1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 11-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09a1.65 1.65 0 001.51-1.08 1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 112.83-2.83l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 114 0v.09a1.65 1.65 0 001.08 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 112.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9c.26.604.852.997 1.51 1H21a2 2 0 110 4h-.09a1.65 1.65 0 00-1.51 1.08z"/></svg>
        Settings
      </router-link>
      <button @click="handleLogout" class="flex w-full items-center gap-2.5 rounded-md px-2.5 py-2 text-sm text-[var(--color-text-muted)] hover:bg-zinc-50">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        Log Out
      </button>
    </div>

    <!-- User Card -->
    <div class="mx-3 mt-2 flex items-center gap-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2.5">
      <div class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-[var(--color-primary)] text-xs font-semibold text-white">
        {{ auth.user?.name?.charAt(0)?.toUpperCase() || 'U' }}
      </div>
      <div class="min-w-0 flex-1">
        <div class="truncate text-sm font-medium text-[var(--color-text)]">{{ auth.user?.name || 'User' }}</div>
        <div class="truncate text-xs text-[var(--color-text-muted)]">{{ auth.user?.email || '' }}</div>
      </div>
    </div>
  </aside>
</template>
