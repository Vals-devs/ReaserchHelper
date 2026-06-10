<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth = useAuthStore()

// Tabs
const activeTab = ref<'profile' | 'preferences'>('profile')

// Profile State
const name = ref(auth.user?.name || '')
const institution = ref(auth.user?.institution || '')
const researchInterests = ref(auth.user?.research_interests || '')
const savingProfile = ref(false)
const profileSuccess = ref('')
const profileError = ref('')

// Password State
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const changingPassword = ref(false)
const passwordSuccess = ref('')
const passwordError = ref('')

// Preferences State (Stored in localStorage)
const selectedModel = ref(localStorage.getItem('settings_ai_model') || 'llama3-70b')
const selectedLanguage = ref(localStorage.getItem('settings_ai_language') || 'id')
const currentTheme = ref(localStorage.getItem('settings_theme') || 'light')
const savingPreferences = ref(false)
const preferencesSuccess = ref('')

onMounted(async () => {
  if (!auth.user) {
    await auth.fetchUser()
  }
  // Initialize profile values after fetch
  name.value = auth.user?.name || ''
  institution.value = auth.user?.institution || ''
  researchInterests.value = auth.user?.research_interests || ''
})

async function saveProfile() {
  if (!name.value.trim()) {
    profileError.value = 'Nama tidak boleh kosong.'
    return
  }
  savingProfile.value = true
  profileError.value = ''
  profileSuccess.value = ''
  try {
    const { data } = await api.put('/auth/profile', {
      name: name.value,
      institution: institution.value,
      research_interests: researchInterests.value,
    })
    auth.user = data
    profileSuccess.value = 'Profil berhasil diperbarui!'
    setTimeout(() => { profileSuccess.value = '' }, 3000)
  } catch (err: any) {
    profileError.value = err.response?.data?.detail || 'Gagal memperbarui profil.'
  } finally {
    savingProfile.value = false
  }
}

async function changePassword() {
  if (!newPassword.value) {
    passwordError.value = 'Password baru tidak boleh kosong.'
    return
  }
  if (newPassword.value.length < 6) {
    passwordError.value = 'Password minimal terdiri dari 6 karakter.'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = 'Konfirmasi password tidak cocok.'
    return
  }
  
  changingPassword.value = true
  passwordError.value = ''
  passwordSuccess.value = ''
  try {
    const { data } = await api.put('/auth/profile', {
      password: newPassword.value,
    })
    auth.user = data
    passwordSuccess.value = 'Password berhasil diubah!'
    newPassword.value = ''
    confirmPassword.value = ''
    setTimeout(() => { passwordSuccess.value = '' }, 3000)
  } catch (err: any) {
    passwordError.value = err.response?.data?.detail || 'Gagal mengubah password.'
  } finally {
    changingPassword.value = false
  }
}

function savePreferences() {
  savingPreferences.value = true
  localStorage.setItem('settings_ai_model', selectedModel.value)
  localStorage.setItem('settings_ai_language', selectedLanguage.value)
  localStorage.setItem('settings_theme', currentTheme.value)
  
  // Apply theme class to document if dark/light
  if (currentTheme.value === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
  
  setTimeout(() => {
    savingPreferences.value = false
    preferencesSuccess.value = 'Preferensi berhasil disimpan!'
    setTimeout(() => { preferencesSuccess.value = '' }, 3000)
  }, 500)
}
</script>

<template>
  <div class="px-6 py-5 w-full">
    <div class="mb-5">
      <h1 class="text-xl font-bold text-[var(--color-text)]">Settings</h1>
      <p class="text-xs text-[var(--color-text-sub)]">Atur preferensi profil, kata sandi, dan parameter kecerdasan buatan (AI) Anda.</p>
    </div>

    <!-- Segmented Navigation Tabs -->
    <div class="flex border-b border-[var(--color-border)] mb-6">
      <button 
        @click="activeTab = 'profile'"
        class="pb-3 px-4 text-sm font-medium transition border-b-2 -mb-px"
        :class="activeTab === 'profile' ? 'border-[var(--color-primary)] text-[var(--color-primary)]' : 'border-transparent text-[var(--color-text-muted)] hover:text-[var(--color-text-sub)]'"
      >
        Profil & Keamanan
      </button>
      <button 
        @click="activeTab = 'preferences'"
        class="pb-3 px-4 text-sm font-medium transition border-b-2 -mb-px"
        :class="activeTab === 'preferences' ? 'border-[var(--color-primary)] text-[var(--color-primary)]' : 'border-transparent text-[var(--color-text-muted)] hover:text-[var(--color-text-sub)]'"
      >
        Preferensi AI & Aplikasi
      </button>
    </div>

    <!-- TAB: PROFILE & SECURITY -->
    <div v-if="activeTab === 'profile'" class="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
      <!-- Profile Card -->
      <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
        <h3 class="text-sm font-semibold text-[var(--color-text)] mb-4 flex items-center gap-1.5">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/></svg>
          Informasi Profil
        </h3>
        
        <div v-if="profileSuccess" class="mb-4 rounded-md bg-emerald-50 border border-emerald-100 p-2.5 text-xs text-emerald-800">
          {{ profileSuccess }}
        </div>
        <div v-if="profileError" class="mb-4 rounded-md bg-red-50 border border-red-100 p-2.5 text-xs text-red-700">
          {{ profileError }}
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-[var(--color-text-sub)] mb-1">Nama Lengkap</label>
            <input 
              v-model="name" 
              type="text" 
              placeholder="Nama Anda..."
              class="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-xs outline-none focus:border-[var(--color-primary)]"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-[var(--color-text-sub)] mb-1">Email (Akun)</label>
            <input 
              :value="auth.user?.email" 
              type="email" 
              disabled
              class="w-full rounded-md border border-[var(--color-border)] bg-zinc-50 px-3 py-2 text-xs text-zinc-500 cursor-not-allowed"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-[var(--color-text-sub)] mb-1">Institusi / Universitas</label>
            <input 
              v-model="institution" 
              type="text" 
              placeholder="cth. Universitas Indonesia"
              class="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-xs outline-none focus:border-[var(--color-primary)]"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-[var(--color-text-sub)] mb-1">Bidang Ketertarikan Riset</label>
            <textarea 
              v-model="researchInterests" 
              rows="3"
              placeholder="cth. Machine Learning, NLP, Data Security"
              class="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-xs outline-none resize-none focus:border-[var(--color-primary)]"
            ></textarea>
          </div>

          <button 
            @click="saveProfile" 
            :disabled="savingProfile"
            class="w-full rounded-md bg-[var(--color-primary)] py-2 text-xs font-medium text-white transition hover:bg-[var(--color-primary-hover)] disabled:opacity-50"
          >
            {{ savingProfile ? 'Menyimpan...' : 'Simpan Profil' }}
          </button>
        </div>
      </div>

      <!-- Password Card -->
      <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
        <h3 class="text-sm font-semibold text-[var(--color-text)] mb-4 flex items-center gap-1.5">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/></svg>
          Keamanan Kata Sandi
        </h3>
        
        <div v-if="passwordSuccess" class="mb-4 rounded-md bg-emerald-50 border border-emerald-100 p-2.5 text-xs text-emerald-800">
          {{ passwordSuccess }}
        </div>
        <div v-if="passwordError" class="mb-4 rounded-md bg-red-50 border border-red-100 p-2.5 text-xs text-red-700">
          {{ passwordError }}
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-[var(--color-text-sub)] mb-1">Password Baru</label>
            <input 
              v-model="newPassword" 
              type="password" 
              placeholder="Masukkan password baru..."
              class="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-xs outline-none focus:border-[var(--color-primary)]"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-[var(--color-text-sub)] mb-1">Konfirmasi Password Baru</label>
            <input 
              v-model="confirmPassword" 
              type="password" 
              placeholder="Konfirmasi password baru..."
              class="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-xs outline-none focus:border-[var(--color-primary)]"
            />
          </div>

          <button 
            @click="changePassword" 
            :disabled="changingPassword"
            class="w-full rounded-md bg-zinc-900 py-2 text-xs font-medium text-white transition hover:bg-zinc-800 disabled:opacity-50"
          >
            {{ changingPassword ? 'Memperbarui...' : 'Ubah Password' }}
          </button>
        </div>
      </div>
    </div>

    <!-- TAB: PREFERENCES -->
    <div v-if="activeTab === 'preferences'" class="max-w-2xl">
      <div class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
        <h3 class="text-sm font-semibold text-[var(--color-text)] mb-4 flex items-center gap-1.5">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9.594 3.94c.09-.542.56-.94 1.11-.94h1.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.43l-1.003.828c-.293.241-.438.613-.43.992a7.723 7.723 0 010 .255c-.008.378.137.75.43.991l1.004.829a1.125 1.125 0 01.26 1.43l-1.297 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-1.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.43l1.004-.828c.292-.242.437-.613.43-.992a7.72 7.72 0 010-.255c.007-.378-.138-.75-.43-.991l-1.004-.83a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.645-.869l.214-1.28z"/><circle cx="12" cy="12" r="3"/></svg>
          Preferensi Aplikasi & AI
        </h3>

        <div v-if="preferencesSuccess" class="mb-4 rounded-md bg-emerald-50 border border-emerald-100 p-2.5 text-xs text-emerald-800">
          {{ preferencesSuccess }}
        </div>

        <div class="space-y-5">
          <!-- AI Model Selection -->
          <div>
            <label class="block text-xs font-semibold text-[var(--color-text-sub)] mb-1.5">Model AI Default (Q&A & Ringkasan)</label>
            <div class="grid grid-cols-2 gap-2">
              <label 
                class="flex flex-col gap-1.5 rounded-lg border p-3 cursor-pointer transition select-none"
                :class="selectedModel === 'llama3-8b' ? 'border-[var(--color-primary)] bg-[var(--color-primary-soft)]' : 'border-[var(--color-border)] hover:border-zinc-300'"
              >
                <div class="flex items-center justify-between">
                  <span class="text-xs font-semibold text-[var(--color-text)]">Llama 3 8B (Fast)</span>
                  <input type="radio" v-model="selectedModel" value="llama3-8b" class="accent-[var(--color-primary)]" />
                </div>
                <p class="text-[10px] text-[var(--color-text-muted)] leading-relaxed">Model AI berkecepatan tinggi, sangat baik untuk prapemrosesan dan ringkasan cepat.</p>
              </label>

              <label 
                class="flex flex-col gap-1.5 rounded-lg border p-3 cursor-pointer transition select-none"
                :class="selectedModel === 'llama3-70b' ? 'border-[var(--color-primary)] bg-[var(--color-primary-soft)]' : 'border-[var(--color-border)] hover:border-zinc-300'"
              >
                <div class="flex items-center justify-between">
                  <span class="text-xs font-semibold text-[var(--color-text)]">Llama 3 70B (Smart)</span>
                  <input type="radio" v-model="selectedModel" value="llama3-70b" class="accent-[var(--color-primary)]" />
                </div>
                <p class="text-[10px] text-[var(--color-text-muted)] leading-relaxed">Model AI akademis mendalam. Sangat disarankan untuk penalaran rumit dan analisis gap.</p>
              </label>
            </div>
          </div>

          <!-- Language Selection -->
          <div>
            <label class="block text-xs font-semibold text-[var(--color-text-sub)] mb-1">Bahasa Respons AI Default</label>
            <select 
              v-model="selectedLanguage"
              class="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-xs outline-none focus:border-[var(--color-primary)]"
            >
              <option value="id">Bahasa Indonesia</option>
              <option value="en">English (US/UK)</option>
            </select>
            <p class="mt-1 text-[10px] text-[var(--color-text-muted)]">AI akan memprioritaskan penyusunan ringkasan dan jawaban obrolan dalam bahasa terpilih.</p>
          </div>

          <!-- Theme Preference -->
          <div>
            <label class="block text-xs font-semibold text-[var(--color-text-sub)] mb-1">Tema Tampilan</label>
            <select 
              v-model="currentTheme"
              class="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-xs outline-none focus:border-[var(--color-primary)]"
            >
              <option value="light">Mode Terang (Light Mode)</option>
              <option value="dark">Mode Gelap (Dark Mode)</option>
            </select>
            <p class="mt-1 text-[10px] text-[var(--color-text-muted)]">Atur tampilan antarmuka yang paling nyaman untuk mata Anda.</p>
          </div>

          <button 
            @click="savePreferences" 
            :disabled="savingPreferences"
            class="w-full rounded-md bg-[var(--color-primary)] py-2 text-xs font-medium text-white transition hover:bg-[var(--color-primary-hover)] disabled:opacity-50"
          >
            {{ savingPreferences ? 'Menyimpan...' : 'Simpan Preferensi' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
