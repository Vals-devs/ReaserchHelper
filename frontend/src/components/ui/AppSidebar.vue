<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const menuItems = [
  { id: 'search', label: 'Search Papers', path: '/search', icon: '🔍' },
  { id: 'collections', label: 'Collections', path: '/collections', icon: '📚' },
  { id: 'history', label: 'Search History', path: '/history', icon: '🕐' },
  { id: 'gap', label: 'Gap Analysis', path: '/gap-analysis', icon: '💡' },
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
  <aside class="fixed left-0 top-0 z-20 flex h-screen w-[252px] flex-col border-r border-[var(--color-border)] bg-[var(--color-surface)] py-5">
    <!-- Brand -->
    <div class="flex items-center gap-3 px-5 pb-6">
      <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[var(--color-primary)] to-blue-400 shadow-sm">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" opacity="0.9" />
          <polyline points="14 2 14 8 20 8" fill="none" stroke="white" stroke-width="1.5" />
        </svg>
      </div>
      <div>
        <div class="text-[15px] font-extrabold tracking-tight text-[var(--color-text)]">ResearchFinder</div>
        <div class="text-[10.5px] font-medium text-[var(--color-text-muted)]">AI-Powered Research Tool</div>
      </div>
    </div>

    <!-- New Search CTA -->
    <div class="px-3 mb-2">
      <router-link
        to="/search"
        class="flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--color-primary)] px-4 py-2.5 text-[13px] font-semibold text-white shadow-sm transition hover:bg-[var(--color-primary-hover)]"
      >
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        New Search
      </router-link>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto px-2.5 py-2">
      <div class="px-3 pb-1.5 text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-muted)]">Navigation</div>
      <router-link
        v-for="item in menuItems"
        :key="item.id"
        :to="item.path"
        class="mb-0.5 flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-[13.5px] transition"
        :class="isActive(item.path) ? 'bg-[var(--color-primary-soft)] font-semibold text-[var(--color-primary)]' : 'font-normal text-[var(--color-text-sub)] hover:bg-gray-50'"
      >
        <span class="text-base">{{ item.icon }}</span>
        {{ item.label }}
      </router-link>
    </nav>

    <!-- Bottom -->
    <div class="border-t border-gray-100 px-2.5 pt-2">
      <router-link to="/" class="flex items-center gap-2.5 rounded-xl px-3 py-2 text-[13px] text-[var(--color-text-muted)] hover:bg-gray-50">
        <span class="text-base">⚙️</span> Settings
      </router-link>
      <button @click="handleLogout" class="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-[13px] text-[var(--color-text-muted)] hover:bg-gray-50">
        <span class="text-base">🚪</span> Log Out
      </button>
    </div>

    <!-- User Card -->
    <div class="mx-3 mt-2 flex items-center gap-2.5 rounded-xl border border-gray-100 bg-[var(--color-bg)] px-3.5 py-3">
      <div class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[var(--color-primary)] to-purple-600 text-xs font-bold text-white">
        IP
      </div>
      <div class="min-w-0 flex-1">
        <div class="truncate text-[13px] font-semibold text-[var(--color-text)]">Ival Permana</div>
        <div class="truncate text-[11px] text-[var(--color-text-muted)]">ival@univ.ac.id</div>
      </div>
    </div>
  </aside>
</template>
