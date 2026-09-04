<template>
  <div class="p-3 bg-[var(--color-bg)] rounded-xl border border-[var(--color-border)] text-xs">
    <div class="flex items-center justify-between mb-2">
      <div class="flex items-center gap-1.5 font-medium text-[var(--color-text-sub)]">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-[var(--color-primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 2.21 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
        </svg>
        <span>Penyimpanan</span>
      </div>
      <span
        class="px-2 py-0.5 text-[10px] uppercase tracking-wider font-bold rounded-full border border-blue-200 bg-blue-50 text-blue-700 flex items-center gap-1"
      >
        <span>UNLIMITED</span>
      </span>
    </div>

    <!-- Progress Bar -->
    <div class="w-full bg-zinc-200 rounded-full h-2 overflow-hidden mb-2">
      <div
        class="h-full transition-all duration-500 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500"
        :style="{ width: `${percentage}%` }"
      ></div>
    </div>

    <div class="flex items-center justify-between text-[11px] text-[var(--color-text-muted)]">
      <span>{{ usedMb }} MB Terpakai</span>
      <span class="font-semibold text-emerald-600">Aktif</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '@/services/api'

const usedMb = ref(0)
const quotaMb = ref(100)
const percentage = ref(0)
const planTier = ref('free')

const barColor = computed(() => {
  if (percentage.value >= 90) return 'bg-red-500'
  if (percentage.value >= 75) return 'bg-amber-400'
  return 'bg-gradient-to-r from-blue-500 to-indigo-500'
})

async function fetchUsage() {
  try {
    const { data } = await api.get('/upload/storage-usage')
    usedMb.value = data.used_mb
    quotaMb.value = data.quota_mb
    percentage.value = data.percentage
    planTier.value = data.plan_tier
  } catch (err) {
    console.error('Failed to fetch storage usage:', err)
  }
}

let timer: any = null

onMounted(() => {
  fetchUsage()
  window.addEventListener('storage-updated', fetchUsage)
  timer = setInterval(fetchUsage, 60000)
})

onUnmounted(() => {
  window.removeEventListener('storage-updated', fetchUsage)
  if (timer) clearInterval(timer)
})
</script>

