import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export interface UploadedPaper {
  id: string
  title: string
  authors: string[]
  year: number | null
  abstract: string | null
  page_count: number | null
  uploaded_at: string
}

export const useUploadStore = defineStore('upload', () => {
  const papers = ref<UploadedPaper[]>([])
  const uploading = ref(false)
  const uploadError = ref('')
  const loading = ref(false)

  async function fetchPapers() {
    loading.value = true
    try {
      const { data } = await api.get('/upload/papers')
      papers.value = data
    } catch (err) {
      console.error('Failed to fetch uploaded papers:', err)
    } finally {
      loading.value = false
    }
  }

  async function uploadPaper(file: File): Promise<UploadedPaper | null> {
    uploading.value = true
    uploadError.value = ''
    try {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await api.post('/upload/pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000, // 2 min for PDF processing + AI
      })
      papers.value.unshift(data)
      return data
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Gagal mengupload file'
      uploadError.value = msg
      return null
    } finally {
      uploading.value = false
    }
  }

  async function deletePaper(id: string) {
    try {
      await api.delete(`/upload/${id}`)
      papers.value = papers.value.filter((p) => p.id !== id)
    } catch (err) {
      console.error('Failed to delete paper:', err)
    }
  }

  return { papers, uploading, uploadError, loading, fetchPapers, uploadPaper, deletePaper }
})
