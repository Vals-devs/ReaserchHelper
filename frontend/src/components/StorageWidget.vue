<template>
  <div class="p-3 bg-slate-800/80 backdrop-blur rounded-xl border border-slate-700/60 text-xs shadow-inner">
    <div class="flex items-center justify-between mb-2">
      <div class="flex items-center gap-1.5 font-medium text-slate-300">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 2.21 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
        </svg>
        <span>Penyimpanan</span>
      </div>
      <span
        :class="planTier === 'pro' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' : 'bg-slate-700 text-slate-300 border-slate-600'"
        class="px-2 py-0.5 text-[10px] uppercase tracking-wider font-bold rounded-full border flex items-center gap-1"
      >
        <svg v-if="planTier === 'pro'" class="w-3 h-3 text-amber-400 fill-amber-400" viewBox="0 0 24 24">
          <path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5zm14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"/>
        </svg>
        <span>{{ planTier === 'pro' ? 'PRO' : 'FREE' }}</span>
      </span>
    </div>

    <!-- Progress Bar -->
    <div class="w-full bg-slate-700/80 rounded-full h-2 overflow-hidden mb-2">
      <div
        class="h-full transition-all duration-500 rounded-full"
        :class="barColor"
        :style="{ width: `${percentage}%` }"
      ></div>
    </div>

    <div class="flex items-center justify-between text-[11px] text-slate-400">
      <span>{{ usedMb }} MB / {{ quotaMb }} MB</span>
      <span class="font-semibold text-slate-300">{{ percentage }}%</span>
    </div>

    <!-- Upgrade Pro Button for Free Tier -->
    <button
      v-if="planTier !== 'pro'"
      @click="showModal = true"
      class="mt-2.5 w-full py-1.5 px-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-bold text-xs rounded-lg transition-all shadow-lg shadow-amber-500/20 flex items-center justify-center gap-1.5 group cursor-pointer"
    >
      <span>Upgrade Ke Pro</span>
      <svg class="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform text-slate-950" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
      </svg>
    </button>

    <!-- Upgrade Modal -->
    <UpgradeModal v-if="showModal" @close="showModal = false" @upgraded="fetchUsage" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import UpgradeModal from './UpgradeModal.vue'

const usedMb = ref(0)
const quotaMb = ref(100)
const percentage = ref(0)
const planTier = ref('free')
const showModal = ref(false)

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

onMounted(() => {
  fetchUsage()
})
</script>
