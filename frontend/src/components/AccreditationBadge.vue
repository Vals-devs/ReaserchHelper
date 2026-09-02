<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  accreditation?: string | null
  journal?: string | null
  source?: string | null
}>()

const badgeInfo = computed(() => {
  const acc = (props.accreditation || '').trim()
  const src = (props.source || '').toLowerCase()

  if (acc.includes('Scopus Q1')) {
    return { label: 'Scopus Q1', type: 'star', style: 'bg-amber-50 text-amber-700 border-amber-200' }
  }
  if (acc.includes('Scopus Q2')) {
    return { label: 'Scopus Q2', type: 'star', style: 'bg-emerald-50 text-emerald-700 border-emerald-200' }
  }
  if (acc.includes('Scopus Q3')) {
    return { label: 'Scopus Q3', type: 'star', style: 'bg-blue-50 text-blue-700 border-blue-200' }
  }
  if (acc.includes('Scopus Q4')) {
    return { label: 'Scopus Q4', type: 'star', style: 'bg-indigo-50 text-indigo-700 border-indigo-200' }
  }
  if (acc.includes('Scopus')) {
    return { label: 'Scopus Indexed', type: 'star', style: 'bg-purple-50 text-purple-700 border-purple-200' }
  }
  if (acc.includes('Sinta 1')) {
    return { label: 'Sinta 1', type: 'flag', style: 'bg-red-50 text-red-700 border-red-200 font-semibold' }
  }
  if (acc.includes('Sinta 2')) {
    return { label: 'Sinta 2', type: 'flag', style: 'bg-red-50 text-red-700 border-red-200' }
  }
  if (acc.includes('Sinta')) {
    return { label: acc, type: 'flag', style: 'bg-rose-50 text-rose-700 border-rose-200' }
  }
  if (acc.includes('arXiv') || src === 'arxiv') {
    return { label: 'arXiv Preprint', type: 'doc', style: 'bg-sky-50 text-sky-700 border-sky-200' }
  }
  if (acc.includes('PDF')) {
    return { label: 'PDF Uploaded', type: 'pdf', style: 'bg-teal-50 text-teal-700 border-teal-200' }
  }

  return { label: acc || 'Scopus Indexed', type: 'star', style: 'bg-zinc-100 text-zinc-700 border-zinc-200' }
})
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[11px] font-medium tracking-wide transition shadow-2xs"
    :class="badgeInfo.style">
    <!-- Star Vector Icon -->
    <svg v-if="badgeInfo.type === 'star'" class="w-3 h-3 text-amber-500 fill-amber-400" viewBox="0 0 24 24">
      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
    </svg>
    <!-- Flag Vector Icon for Sinta -->
    <svg v-else-if="badgeInfo.type === 'flag'" class="w-3 h-3 text-red-600 fill-current" viewBox="0 0 24 24">
      <path d="M14.4 6L14 4H5v17h2v-7h5.6l.4 2h7V6h-5.6z"/>
    </svg>
    <!-- Doc Vector Icon for arXiv -->
    <svg v-else-if="badgeInfo.type === 'doc'" class="w-3 h-3 text-sky-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/>
      <path d="M14 2v6h6"/>
    </svg>
    <!-- PDF Vector Icon -->
    <svg v-else-if="badgeInfo.type === 'pdf'" class="w-3 h-3 text-teal-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
      <path d="M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
      <path d="M9 7h6M9 11h6M9 15h4"/>
    </svg>
    {{ badgeInfo.label }}
  </span>
</template>
