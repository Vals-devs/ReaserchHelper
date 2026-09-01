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
    return { label: '⭐ Scopus Q1', style: 'bg-amber-50 text-amber-700 border-amber-200' }
  }
  if (acc.includes('Scopus Q2')) {
    return { label: 'Scopus Q2', style: 'bg-emerald-50 text-emerald-700 border-emerald-200' }
  }
  if (acc.includes('Scopus Q3')) {
    return { label: 'Scopus Q3', style: 'bg-blue-50 text-blue-700 border-blue-200' }
  }
  if (acc.includes('Scopus Q4')) {
    return { label: 'Scopus Q4', style: 'bg-indigo-50 text-indigo-700 border-indigo-200' }
  }
  if (acc.includes('Scopus')) {
    return { label: 'Scopus Indexed', style: 'bg-purple-50 text-purple-700 border-purple-200' }
  }
  if (acc.includes('Sinta 1')) {
    return { label: '🇮🇩 Sinta 1', style: 'bg-red-50 text-red-700 border-red-200 font-semibold' }
  }
  if (acc.includes('Sinta 2')) {
    return { label: '🇮🇩 Sinta 2', style: 'bg-red-50 text-red-700 border-red-200' }
  }
  if (acc.includes('Sinta')) {
    return { label: `🇮🇩 ${acc}`, style: 'bg-rose-50 text-rose-700 border-rose-200' }
  }
  if (acc.includes('arXiv') || src === 'arxiv') {
    return { label: 'arXiv Preprint', style: 'bg-sky-50 text-sky-700 border-sky-200' }
  }
  if (acc.includes('PDF')) {
    return { label: 'PDF Uploaded', style: 'bg-teal-50 text-teal-700 border-teal-200' }
  }

  return { label: acc || 'Scopus Indexed', style: 'bg-zinc-100 text-zinc-700 border-zinc-200' }
})
</script>

<template>
  <span
    class="inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[11px] font-medium tracking-wide transition shadow-2xs"
    :class="badgeInfo.style">
    {{ badgeInfo.label }}
  </span>
</template>
