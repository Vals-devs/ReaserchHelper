<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const name = ref('')
const email = ref('')
const password = ref('')
const institution = ref('')
const error = ref('')
const fieldErrors = ref<Record<string, string>>({})
const loading = ref(false)

function getErrorMessage(e: any): string {
  // Network error (backend not reachable)
  if (!e.response) {
    return 'Tidak bisa terhubung ke server. Pastikan backend sudah berjalan di port 8000.'
  }

  const status = e.response.status
  const data = e.response.data

  // Validation errors from FastAPI (422)
  if (status === 422 && data?.detail) {
    if (Array.isArray(data.detail)) {
      const errors: Record<string, string> = {}
      for (const err of data.detail) {
        const field = err.loc?.[err.loc.length - 1] || 'unknown'
        errors[field] = err.msg || 'Invalid value'
      }
      fieldErrors.value = errors
      return 'Ada field yang tidak valid. Periksa form di bawah.'
    }
    return data.detail
  }

  // Business logic errors (400, 409)
  if (data?.detail) return data.detail

  // Server errors
  if (status >= 500) return 'Terjadi kesalahan pada server. Coba lagi nanti.'

  return `Registrasi gagal (error ${status})`
}

async function handleRegister() {
  error.value = ''
  fieldErrors.value = {}
  loading.value = true
  try {
    await auth.register({
      name: name.value,
      email: email.value,
      password: password.value,
      institution: institution.value || undefined,
    })
    router.push('/')
  } catch (e: any) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-[var(--color-bg)]">
    <div class="w-full max-w-[400px] px-4">
      <!-- Logo -->
      <div class="mb-6 flex items-center justify-center gap-2.5">
        <img src="@/assets/logo.png" class="h-12 w-12 object-contain rounded-md" alt="ResearchFinder Logo" />
        <div class="text-lg font-bold text-[var(--color-text)]">ResearchFinder</div>
      </div>

      <!-- Card -->
      <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-6">
        <h2 class="text-center text-base font-semibold text-[var(--color-text)]">Buat Akun Baru</h2>
        <p class="mb-5 mt-1 text-center text-sm text-[var(--color-text-sub)]">Mulai perjalanan riset kamu di sini</p>

        <!-- Error banner -->
        <div v-if="error" class="mb-4 rounded-md bg-red-50 border border-red-200 px-3 py-2">
          <div class="flex items-start gap-2">
            <svg width="16" height="16" class="mt-0.5 flex-shrink-0 text-red-500" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>
            <div class="text-sm text-red-700 leading-relaxed">{{ error }}</div>
          </div>
        </div>

        <form @submit.prevent="handleRegister">
          <div class="mb-3">
            <label class="mb-1 block text-sm font-medium text-[var(--color-text)]">Nama Lengkap</label>
            <input v-model="name" type="text" required placeholder="Your full name"
              class="w-full rounded-md border px-3 py-2 text-sm outline-none transition focus:border-[var(--color-primary)] focus:ring-1 focus:ring-[var(--color-primary)]/20"
              :class="fieldErrors.name ? 'border-red-400 bg-red-50' : 'border-[var(--color-border)] bg-[var(--color-bg)]'" />
            <p v-if="fieldErrors.name" class="mt-0.5 text-xs text-red-500">{{ fieldErrors.name }}</p>
          </div>
          <div class="mb-3">
            <label class="mb-1 block text-sm font-medium text-[var(--color-text)]">Email</label>
            <input v-model="email" type="email" required placeholder="you@example.com"
              class="w-full rounded-md border px-3 py-2 text-sm outline-none transition focus:border-[var(--color-primary)] focus:ring-1 focus:ring-[var(--color-primary)]/20"
              :class="fieldErrors.email ? 'border-red-400 bg-red-50' : 'border-[var(--color-border)] bg-[var(--color-bg)]'" />
            <p v-if="fieldErrors.email" class="mt-0.5 text-xs text-red-500">{{ fieldErrors.email }}</p>
          </div>
          <div class="mb-3">
            <label class="mb-1 block text-sm font-medium text-[var(--color-text)]">Password</label>
            <input v-model="password" type="password" required placeholder="Minimum 8 characters"
              class="w-full rounded-md border px-3 py-2 text-sm outline-none transition focus:border-[var(--color-primary)] focus:ring-1 focus:ring-[var(--color-primary)]/20"
              :class="fieldErrors.password ? 'border-red-400 bg-red-50' : 'border-[var(--color-border)] bg-[var(--color-bg)]'" />
            <p v-if="fieldErrors.password" class="mt-0.5 text-xs text-red-500">{{ fieldErrors.password }}</p>
          </div>
          <div class="mb-5">
            <label class="mb-1 block text-sm font-medium text-[var(--color-text)]">
              Institusi / Universitas <span class="text-[var(--color-text-muted)]">(opsional)</span>
            </label>
            <input v-model="institution" type="text" placeholder="Your university or institution"
              class="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-sm outline-none transition focus:border-[var(--color-primary)] focus:ring-1 focus:ring-[var(--color-primary)]/20" />
          </div>
          <button type="submit" :disabled="loading" class="w-full rounded-md bg-[var(--color-primary)] py-2 text-sm font-medium text-white transition hover:bg-[var(--color-primary-hover)] disabled:opacity-50">
            {{ loading ? 'Mendaftarkan...' : 'Daftar Sekarang' }}
          </button>
        </form>
      </div>

      <p class="mt-4 text-center text-sm text-[var(--color-text-sub)]">
        Sudah punya akun? <router-link to="/login" class="font-medium text-[var(--color-primary)]">Masuk di sini</router-link>
      </p>
    </div>
  </div>
</template>
