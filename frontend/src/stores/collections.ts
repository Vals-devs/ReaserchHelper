import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export interface Collection {
  id: string
  user_id: string
  name: string
  description: string | null
  is_public: boolean
  created_at: string
  paper_count: number
}

export interface CollectionPaper {
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
  page_count: number | null
  notes: string | null
  highlights: any[]
  added_at: string | null
}

export interface CollectionDetail extends Collection {
  papers: CollectionPaper[]
}

export const useCollectionsStore = defineStore('collections', () => {
  const collections = ref<Collection[]>([])
  const loading = ref(false)

  async function fetchCollections() {
    loading.value = true
    try {
      const { data } = await api.get('/collections/')
      collections.value = data
    } catch (err) {
      console.error('Failed to fetch collections:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchCollectionDetail(collectionId: string): Promise<CollectionDetail | null> {
    try {
      const { data } = await api.get(`/collections/${collectionId}`)
      return data
    } catch (err) {
      console.error('Failed to fetch collection detail:', err)
      return null
    }
  }

  async function createCollection(name: string, description?: string) {
    const { data } = await api.post('/collections/', { name, description })
    collections.value.unshift(data)
    return data
  }

  async function deleteCollection(id: string) {
    await api.delete(`/collections/${id}`)
    collections.value = collections.value.filter((c) => c.id !== id)
  }

  async function removePaperFromCollection(collectionId: string, paperId: string) {
    await api.delete(`/collections/${collectionId}/papers/${paperId}`)
    // Update paper count locally
    const col = collections.value.find((c) => c.id === collectionId)
    if (col && col.paper_count > 0) col.paper_count--
  }

  async function updatePaperNotes(collectionId: string, paperId: string, notes: string) {
    await api.put(`/collections/${collectionId}/papers/${paperId}/notes`, null, {
      params: { notes },
    })
  }

  return {
    collections, loading,
    fetchCollections, fetchCollectionDetail, createCollection, deleteCollection,
    removePaperFromCollection, updatePaperNotes,
  }
})
