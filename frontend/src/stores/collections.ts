import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

interface Collection {
  id: string
  user_id: string
  name: string
  description: string | null
  is_public: boolean
  created_at: string
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

  async function createCollection(name: string, description?: string) {
    const { data } = await api.post('/collections/', { name, description })
    collections.value.unshift(data)
    return data
  }

  async function deleteCollection(id: string) {
    await api.delete(`/collections/${id}`)
    collections.value = collections.value.filter((c) => c.id !== id)
  }

  return { collections, loading, fetchCollections, createCollection, deleteCollection }
})
