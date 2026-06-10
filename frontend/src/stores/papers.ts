import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export interface Paper {
  id: string
  external_id: string
  source: string
  title: string
  authors: string[]
  abstract: string | null
  year: number | null
  doi: string | null
  url: string | null
  citation_count: number
  fields_of_study: string[]
}

export const usePapersStore = defineStore('papers', () => {
  const results = ref<Paper[]>([])
  const loading = ref(false)
  const total = ref(0)
  const query = ref('')
  const sources = ref<{ semantic_scholar: number; arxiv: number }>({ semantic_scholar: 0, arxiv: 0 })
  const errors = ref<string[]>([])
  const error = ref('')

  async function search(q: string, filters?: Record<string, string>) {
    loading.value = true
    query.value = q
    error.value = ''
    errors.value = []
    try {
      const { data } = await api.get('/papers/search', { params: { q, ...filters } })
      results.value = data.results
      total.value = data.total
      sources.value = data.sources || { semantic_scholar: 0, arxiv: 0 }
      errors.value = data.errors || []
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Pencarian gagal'
      error.value = msg
      results.value = []
    } finally {
      loading.value = false
    }
  }

  async function savePaper(paper: Paper) {
    // Save paper to a collection (future: pick collection)
    try {
      await api.post('/collections/default/papers', { paper_id: paper.id })
    } catch (err) {
      console.error('Failed to save paper:', err)
    }
  }

  return { results, loading, total, query, sources, errors, error, search, savePaper }
})
