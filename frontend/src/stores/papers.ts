import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

interface Paper {
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

  async function search(q: string, filters?: Record<string, string>) {
    loading.value = true
    query.value = q
    try {
      const { data } = await api.get('/papers/search', { params: { q, ...filters } })
      results.value = data.results
      total.value = data.total
    } catch (err) {
      console.error('Search failed:', err)
      results.value = []
    } finally {
      loading.value = false
    }
  }

  return { results, loading, total, query, search }
})
