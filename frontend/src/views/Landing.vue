<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

function getStarted() {
  if (auth.isAuthenticated) {
    router.push('/dashboard')
  } else {
    router.push('/register')
  }
}
</script>

<template>
  <div class="min-h-screen bg-[var(--color-bg)]">
    <!-- Navbar -->
    <nav class="sticky top-0 z-50 border-b border-[var(--color-border)] bg-[var(--color-surface)]/80 backdrop-blur-xl">
      <div class="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[var(--color-primary)] to-blue-400 shadow-sm">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="white"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" opacity="0.9"/><polyline points="14 2 14 8 20 8" fill="none" stroke="white" stroke-width="1.5"/></svg>
          </div>
          <span class="text-[17px] font-extrabold tracking-tight text-[var(--color-text)]">ResearchFinder</span>
        </div>
        <div class="flex items-center gap-3">
          <router-link to="/login" class="rounded-xl px-4 py-2 text-[13px] font-semibold text-[var(--color-text-sub)] transition hover:text-[var(--color-text)]">
            Masuk
          </router-link>
          <button @click="getStarted"
            class="rounded-xl bg-[var(--color-primary)] px-5 py-2.5 text-[13px] font-semibold text-white shadow-sm transition hover:bg-[var(--color-primary-hover)]">
            Mulai Gratis
          </button>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-b from-[var(--color-primary-soft)]/50 to-transparent"></div>
      <div class="relative mx-auto max-w-4xl px-6 pb-20 pt-24 text-center">
        <div class="mb-5 inline-flex items-center gap-2 rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-1.5 text-[12px] font-medium text-[var(--color-text-sub)]">
          <span class="h-2 w-2 rounded-full bg-green-500"></span>
          Powered by AI · 100% Gratis untuk Mahasiswa
        </div>
        <h1 class="text-4xl font-extrabold leading-[1.15] tracking-tight text-[var(--color-text)] sm:text-5xl lg:text-6xl">
          Temukan & Pahami<br>
          <span class="bg-gradient-to-r from-[var(--color-primary)] to-purple-600 bg-clip-text text-transparent">Paper Ilmiah</span>
          <br>dengan Bantuan AI
        </h1>
        <p class="mx-auto mt-6 max-w-2xl text-[17px] leading-relaxed text-[var(--color-text-sub)]">
          Platform riset akademik yang membantu mahasiswa menemukan, meringkas, dan menganalisis paper ilmiah
          dari <strong>Semantic Scholar</strong> dan <strong>arXiv</strong> — dilengkapi AI summarizer,
          research gap analyzer, dan terjemahan otomatis ke bahasa Indonesia.
        </p>
        <div class="mt-8 flex items-center justify-center gap-3">
          <button @click="getStarted"
            class="rounded-xl bg-[var(--color-primary)] px-7 py-3.5 text-[15px] font-bold text-white shadow-lg shadow-blue-200 transition hover:bg-[var(--color-primary-hover)] hover:shadow-xl">
            Mulai Sekarang — Gratis
          </button>
          <router-link to="/login"
            class="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] px-6 py-3.5 text-[15px] font-semibold text-[var(--color-text-sub)] transition hover:bg-gray-50">
            Sudah punya akun?
          </router-link>
        </div>
        <p class="mt-4 text-[12px] text-[var(--color-text-muted)]">Tidak perlu kartu kredit · Daftar dalam 30 detik</p>
      </div>
    </section>

    <!-- Features -->
    <section class="mx-auto max-w-6xl px-6 pb-20">
      <div class="mb-12 text-center">
        <h2 class="text-2xl font-extrabold text-[var(--color-text)] sm:text-3xl">Fitur Unggulan</h2>
        <p class="mt-2 text-[15px] text-[var(--color-text-sub)]">Semua yang kamu butuhkan untuk riset skripsi dan tugas akhir</p>
      </div>

      <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <!-- Feature 1 -->
        <div class="group rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 transition hover:border-[var(--color-primary)] hover:shadow-lg">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--color-primary-soft)] text-2xl">🔍</div>
          <h3 class="text-[16px] font-bold text-[var(--color-text)]">Pencarian Multi-Sumber</h3>
          <p class="mt-2 text-[13.5px] leading-relaxed text-[var(--color-text-sub)]">
            Cari paper dari <strong>Semantic Scholar</strong> dan <strong>arXiv</strong> sekaligus dalam satu query. Dilengkapi filter bidang studi, tahun, dan jumlah sitasi.
          </p>
          <div class="mt-4 flex flex-wrap gap-1.5">
            <span class="rounded-full bg-[var(--color-primary-soft)] px-2.5 py-0.5 text-[10px] font-semibold text-[var(--color-primary)]">Semantic Scholar</span>
            <span class="rounded-full bg-purple-50 px-2.5 py-0.5 text-[10px] font-semibold text-purple-600">arXiv</span>
            <span class="rounded-full bg-green-50 px-2.5 py-0.5 text-[10px] font-semibold text-green-600">Auto-cache</span>
          </div>
        </div>

        <!-- Feature 2 -->
        <div class="group rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 transition hover:border-purple-300 hover:shadow-lg">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-purple-50 text-2xl">🤖</div>
          <h3 class="text-[16px] font-bold text-[var(--color-text)]">AI Paper Summarizer</h3>
          <p class="mt-2 text-[13.5px] leading-relaxed text-[var(--color-text-sub)]">
            Ringkasan otomatis paper dalam <strong>bahasa Indonesia</strong> yang mudah dipahami. Termasuk temuan utama, metodologi, dan kontribusi paper.
          </p>
          <div class="mt-4 flex flex-wrap gap-1.5">
            <span class="rounded-full bg-purple-50 px-2.5 py-0.5 text-[10px] font-semibold text-purple-600">Groq AI</span>
            <span class="rounded-full bg-blue-50 px-2.5 py-0.5 text-[10px] font-semibold text-blue-600">Bahasa Indonesia</span>
          </div>
        </div>

        <!-- Feature 3 -->
        <div class="group rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 transition hover:border-red-200 hover:shadow-lg">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-red-50 text-2xl">💡</div>
          <h3 class="text-[16px] font-bold text-[var(--color-text)]">Research Gap Analyzer</h3>
          <p class="mt-2 text-[13.5px] leading-relaxed text-[var(--color-text-sub)]">
            Analisis <strong>celah penelitian</strong> dari paper-paper yang kamu kumpulkan. AI identifikasi topik yang sudah jenuh, metodologi dominan, dan saran topik baru.
          </p>
          <div class="mt-4 flex flex-wrap gap-1.5">
            <span class="rounded-full bg-red-50 px-2.5 py-0.5 text-[10px] font-semibold text-red-500">Gap Detection</span>
            <span class="rounded-full bg-amber-50 px-2.5 py-0.5 text-[10px] font-semibold text-amber-600">Multi-paper</span>
          </div>
        </div>

        <!-- Feature 4 -->
        <div class="group rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 transition hover:border-green-200 hover:shadow-lg">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-green-50 text-2xl">📄</div>
          <h3 class="text-[16px] font-bold text-[var(--color-text)]">Upload PDF + AI Extract</h3>
          <p class="mt-2 text-[13.5px] leading-relaxed text-[var(--color-text-sub)]">
            Upload paper PDF yang kamu download sendiri. AI akan <strong>extract metadata otomatis</strong> — judul, penulis, tahun, dan abstrak.
          </p>
          <div class="mt-4 flex flex-wrap gap-1.5">
            <span class="rounded-full bg-green-50 px-2.5 py-0.5 text-[10px] font-semibold text-green-600">PyMuPDF</span>
            <span class="rounded-full bg-blue-50 px-2.5 py-0.5 text-[10px] font-semibold text-blue-600">Auto-extract</span>
          </div>
        </div>

        <!-- Feature 5 -->
        <div class="group rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 transition hover:border-amber-200 hover:shadow-lg">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-amber-50 text-2xl">🌐</div>
          <h3 class="text-[16px] font-bold text-[var(--color-text)]">Terjemahan Abstrak</h3>
          <p class="mt-2 text-[13.5px] leading-relaxed text-[var(--color-text-sub)]">
            Abstrak bahasa Inggris yang sulit dipahami? <strong>Terjemahkan ke bahasa Indonesia</strong> dengan satu klik. Istilah teknis tetap dipertahankan.
          </p>
          <div class="mt-4 flex flex-wrap gap-1.5">
            <span class="rounded-full bg-amber-50 px-2.5 py-0.5 text-[10px] font-semibold text-amber-600">AI Translation</span>
            <span class="rounded-full bg-blue-50 px-2.5 py-0.5 text-[10px] font-semibold text-blue-600">Academic Style</span>
          </div>
        </div>

        <!-- Feature 6 -->
        <div class="group rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 transition hover:border-indigo-200 hover:shadow-lg">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50 text-2xl">📚</div>
          <h3 class="text-[16px] font-bold text-[var(--color-text)]">Koleksi & Catatan</h3>
          <p class="mt-2 text-[13.5px] leading-relaxed text-[var(--color-text-sub)]">
            Simpan paper ke <strong>koleksi terorganisir</strong>, tambahkan catatan pribadi per paper. Sempurna untuk menyusun bab 2 skripsi.
          </p>
          <div class="mt-4 flex flex-wrap gap-1.5">
            <span class="rounded-full bg-indigo-50 px-2.5 py-0.5 text-[10px] font-semibold text-indigo-600">Folders</span>
            <span class="rounded-full bg-pink-50 px-2.5 py-0.5 text-[10px] font-semibold text-pink-500">Notes</span>
          </div>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section class="border-t border-[var(--color-border)] bg-[var(--color-surface)] py-20">
      <div class="mx-auto max-w-4xl px-6">
        <div class="mb-12 text-center">
          <h2 class="text-2xl font-extrabold text-[var(--color-text)] sm:text-3xl">Cara Kerja</h2>
          <p class="mt-2 text-[15px] text-[var(--color-text-sub)]">3 langkah mudah untuk memulai riset kamu</p>
        </div>

        <div class="grid gap-8 sm:grid-cols-3">
          <div class="text-center">
            <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--color-primary)] text-xl font-extrabold text-white shadow-lg shadow-blue-200">1</div>
            <h3 class="text-[15px] font-bold text-[var(--color-text)]">Cari atau Upload</h3>
            <p class="mt-2 text-[13px] text-[var(--color-text-sub)]">
              Cari paper dari database akademik atau upload PDF yang sudah kamu download.
            </p>
          </div>
          <div class="text-center">
            <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-purple-600 text-xl font-extrabold text-white shadow-lg shadow-purple-200">2</div>
            <h3 class="text-[15px] font-bold text-[var(--color-text)]">Pahami dengan AI</h3>
            <p class="mt-2 text-[13px] text-[var(--color-text-sub)]">
              Gunakan AI Summarizer, terjemahan, dan penjelas teks untuk memahami paper dengan cepat.
            </p>
          </div>
          <div class="text-center">
            <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-green-600 text-xl font-extrabold text-white shadow-lg shadow-green-200">3</div>
            <h3 class="text-[15px] font-bold text-[var(--color-text)]">Analisis Gap</h3>
            <p class="mt-2 text-[13px] text-[var(--color-text-sub)]">
              Kumpulkan paper ke koleksi, lalu jalankan Research Gap Analyzer untuk menemukan celah riset.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Tech stack -->
    <section class="mx-auto max-w-4xl px-6 py-16">
      <div class="text-center mb-8">
        <h2 class="text-xl font-extrabold text-[var(--color-text)]">Dibangun dengan Teknologi Terbaik</h2>
      </div>
      <div class="flex flex-wrap items-center justify-center gap-3">
        <span v-for="tech in ['Vue 3', 'TypeScript', 'FastAPI', 'Tailwind CSS', 'Groq AI', 'Semantic Scholar', 'arXiv', 'PyMuPDF', 'PostgreSQL', 'Redis', 'Docker']"
          :key="tech"
          class="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-2 text-[13px] font-semibold text-[var(--color-text-sub)] transition hover:border-[var(--color-primary)] hover:text-[var(--color-primary)]">
          {{ tech }}
        </span>
      </div>
    </section>

    <!-- CTA -->
    <section class="border-t border-[var(--color-border)] bg-gradient-to-b from-[var(--color-primary-soft)]/30 to-transparent py-20">
      <div class="mx-auto max-w-2xl px-6 text-center">
        <h2 class="text-2xl font-extrabold text-[var(--color-text)] sm:text-3xl">Siap Memulai Riset Kamu?</h2>
        <p class="mt-3 text-[15px] text-[var(--color-text-sub)]">
          Bergabung dengan mahasiswa Indonesia yang menggunakan AI untuk mempercepat penelitian mereka.
        </p>
        <button @click="getStarted"
          class="mt-8 rounded-xl bg-[var(--color-primary)] px-8 py-4 text-[16px] font-bold text-white shadow-lg shadow-blue-200 transition hover:bg-[var(--color-primary-hover)] hover:shadow-xl">
          Daftar Gratis Sekarang
        </button>
        <p class="mt-3 text-[12px] text-[var(--color-text-muted)]">Open source · Tidak ada biaya tersembunyi</p>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-[var(--color-border)] bg-[var(--color-surface)] py-8">
      <div class="mx-auto max-w-6xl px-6 flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
        <div class="flex items-center gap-2">
          <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-[var(--color-primary)] to-blue-400">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="white"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" opacity="0.9"/></svg>
          </div>
          <span class="text-[14px] font-bold text-[var(--color-text)]">ResearchFinder</span>
        </div>
        <p class="text-[12px] text-[var(--color-text-muted)]">
          © 2026 ResearchFinder · Dibuat dengan ❤️ untuk mahasiswa Indonesia
        </p>
      </div>
    </footer>
  </div>
</template>
