<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

function getErrorMessage(e: any): string {
  if (!e.response) {
    return 'Tidak bisa terhubung ke server. Pastikan backend sudah berjalan di port 8000.'
  }
  const status = e.response.status
  const data = e.response.data
  if (data?.detail) return data.detail
  if (status === 422) return 'Email atau password tidak valid.'
  if (status >= 500) return 'Terjadi kesalahan pada server. Coba lagi nanti.'
  return `Login gagal (error ${status})`
}

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
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
    <div class="w-full max-w-[380px] px-4">
      <!-- Logo -->
      <div class="mb-6 flex items-center justify-center gap-2.5">
        <img src="@/assets/logo.png" class="h-12 w-12 object-contain rounded-md" alt="ResearchFinder Logo" />
        <div class="text-lg font-bold text-[var(--color-text)]">ResearchFinder</div>
      </div>

      <!-- Card -->
      <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-6">
        <h2 class="text-center text-base font-semibold text-[var(--color-text)]">Selamat Datang Kembali</h2>
        <p class="mb-5 mt-1 text-center text-sm text-[var(--color-text-sub)]">Masuk ke akun ResearchFinder kamu</p>

        <!-- Error banner -->
        <div v-if="error" class="mb-4 rounded-md bg-red-50 border border-red-200 px-3 py-2">
          <div class="flex items-start gap-2">
            <svg width="16" height="16" class="mt-0.5 flex-shrink-0 text-red-500" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>
            <div class="text-sm text-red-700 leading-relaxed">{{ error }}</div>
          </div>
        </div>

        <form @submit.prevent="handleLogin">
          <div class="mb-3.5">
            <label class="mb-1 block text-sm font-medium text-[var(--color-text)]">Email</label>
            <input v-model="email" type="email" required placeholder="you@example.com"
              class="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-sm outline-none transition focus:border-[var(--color-primary)] focus:ring-1 focus:ring-[var(--color-primary)]/20" />
          </div>
          <div class="mb-5">
            <label class="mb-1 block text-sm font-medium text-[var(--color-text)]">Password</label>
            <input v-model="password" type="password" required placeholder="Enter your password"
              class="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-sm outline-none transition focus:border-[var(--color-primary)] focus:ring-1 focus:ring-[var(--color-primary)]/20" />
          </div>
          <button type="submit" :disabled="loading" class="w-full rounded-md bg-[var(--color-primary)] py-2 text-sm font-medium text-white transition hover:bg-[var(--color-primary-hover)] disabled:opacity-50">
            {{ loading ? 'Memproses...' : 'Masuk' }}
          </button>
        </form>
      </div>

      <p class="mt-4 text-center text-sm text-[var(--color-text-sub)]">
        Belum punya akun? <router-link to="/register" class="font-medium text-[var(--color-primary)]">Daftar gratis</router-link>
      </p>
    </div>
  </div>
</template>
