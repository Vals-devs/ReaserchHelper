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
    <div class="w-full max-w-[380px]">
      <!-- Logo -->
      <div class="mb-7 flex items-center justify-center gap-2.5">
        <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--color-primary)]">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="white"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" opacity="0.9"/></svg>
        </div>
        <div class="text-[18px] font-extrabold text-[var(--color-text)]">ResearchFinder</div>
      </div>

      <!-- Card -->
      <div class="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-7 shadow-sm">
        <h2 class="text-center text-lg font-bold text-[var(--color-text)]">Selamat Datang Kembali</h2>
        <p class="mb-6 mt-1.5 text-center text-[13px] text-[var(--color-text-sub)]">Masuk ke akun ResearchFinder kamu</p>

        <!-- Error banner -->
        <div v-if="error" class="mb-4 rounded-lg bg-red-50 border border-red-200 px-3.5 py-2.5">
          <div class="flex items-start gap-2">
            <span class="text-red-500 mt-0.5">⚠️</span>
            <div class="text-[13px] text-red-700 leading-relaxed">{{ error }}</div>
          </div>
        </div>

        <form @submit.prevent="handleLogin">
          <div class="mb-4">
            <label class="mb-1.5 block text-[13px] font-medium text-[var(--color-text)]">Email</label>
            <input v-model="email" type="email" required placeholder="nama@universitas.ac.id"
              class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-bg)] px-3.5 py-2.5 text-[13.5px] outline-none transition focus:border-[var(--color-primary)]" />
          </div>
          <div class="mb-5">
            <label class="mb-1.5 block text-[13px] font-medium text-[var(--color-text)]">Password</label>
            <input v-model="password" type="password" required placeholder="Masukkan password"
              class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-bg)] px-3.5 py-2.5 text-[13.5px] outline-none transition focus:border-[var(--color-primary)]" />
          </div>
          <button type="submit" :disabled="loading" class="w-full rounded-xl bg-[var(--color-primary)] py-2.5 text-sm font-semibold text-white transition hover:bg-[var(--color-primary-hover)] disabled:opacity-50">
            {{ loading ? 'Memproses...' : 'Masuk' }}
          </button>
        </form>
      </div>

      <p class="mt-5 text-center text-[13px] text-[var(--color-text-sub)]">
        Belum punya akun? <router-link to="/register" class="font-semibold text-[var(--color-primary)]">Daftar gratis</router-link>
      </p>
    </div>
  </div>
</template>
