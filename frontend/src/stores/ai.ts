import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useAIStore = defineStore('ai', () => {
  const summary = ref<Record<string, unknown> | null>(null)
  const explanation = ref<string>('')
  const gapResult = ref<Record<string, unknown> | null>(null)
  const loading = ref(false)

  async function summarize(paperId: string) {
    loading.value = true
    try {
      const { data } = await api.post('/ai/summarize', { paper_id: paperId })
      summary.value = data.summary || data
    } finally {
      loading.value = false
    }
  }

  async function explain(text: string, language: string = 'id') {
    loading.value = true
    try {
      const { data } = await api.post('/ai/explain', { text, language })
      explanation.value = data.explanation
    } finally {
      loading.value = false
    }
  }

  async function analyzeGaps(paperIds: string[]) {
    loading.value = true
    try {
      const { data } = await api.post('/ai/gap-analysis', { paper_ids: paperIds })
      gapResult.value = data.gaps || data
    } finally {
      loading.value = false
    }
  }

  return { summary, explanation, gapResult, loading, summarize, explain, analyzeGaps }
})
