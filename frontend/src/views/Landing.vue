<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
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

// Scroll-triggered reveal animation
onMounted(() => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible')
        }
      })
    },
    { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
  )

  document.querySelectorAll('.reveal').forEach((el) => observer.observe(el))

  onUnmounted(() => observer.disconnect())
})

// Interactive Demo State
const activeDemoTab = ref<'search' | 'summary' | 'gap' | 'bib'>('search')

// 1. Search Demo State
const searchDemoQuery = ref('deep learning in healthcare')
const searchDemoResults = ref([
  { source: 'semantic_scholar', title: 'Deep Learning for Healthcare Applications: A Review', year: 2024, cites: 142, saved: false },
  { source: 'arxiv', title: 'A Survey on Deep Learning in Medical Informatics', year: 2025, cites: 68, saved: false }
])
function toggleSaveDemoPaper(index: number) {
  searchDemoResults.value[index].saved = !searchDemoResults.value[index].saved
}

// 2. Summary Demo State
const isSummarizingDemo = ref(false)
const summaryDemoResult = ref<any>(null)
function runSummaryDemo() {
  if (isSummarizingDemo.value) return
  isSummarizingDemo.value = true
  summaryDemoResult.value = null
  
  setTimeout(() => {
    summaryDemoResult.value = {
      ringkasan: "Penelitian ini mengulas penerapan algoritma deep learning dalam menganalisis data rekam medis elektronik untuk memprediksi risiko penyakit kronis pasien secara dini.",
      temuan_utama: [
        "Akurasi deteksi penyakit kronis meningkat hingga 18.4% dibandingkan metode manual.",
        "Model berbasis Transformer menunjukkan performa terbaik untuk data sekuensial klinis.",
        "Tantangan utama terletak pada kurangnya standarisasi format data antar fasilitas kesehatan."
      ],
      metodologi: "Studi literatur komparatif terhadap 45 model klinis berbasis neural networks (2020-2024)."
    }
    isSummarizingDemo.value = false
  }, 1000)
}

// 3. Gap Matrix Demo State
const selectedGapQuadrant = ref<'q1' | 'q2' | 'q3' | 'q4'>('q1')
const gapQuadrants = {
  q1: { title: "Goldmine (Peluang Utama)", badge: "Prioritas Tinggi · Bahasan Jarang", desc: "Penerapan model federated learning pada klasifikasi rekam medis lokal untuk menjaga privasi pasien tanpa transmisi data mentah." },
  q2: { title: "Kompetitif (Mainstream)", badge: "Prioritas Tinggi · Bahasan Sering", desc: "Penggunaan Convolutional Neural Networks (CNN) standar untuk klasifikasi citra sinar-X dada (sudah sangat jenuh dibahas)." },
  q3: { title: "Niche (Eksploratif)", badge: "Prioritas Sedang · Bahasan Jarang", desc: "Analisis sentiment pasien terhadap pelayanan klinik menggunakan model pemrosesan bahasa alami (NLP) berbasis dialek lokal." },
  q4: { title: "Kolektif (Umum)", badge: "Prioritas Sedang · Bahasan Sering", desc: "Penggunaan random forest untuk memprediksi lama rawat inap pasien berdasarkan data administrasi rumah sakit." }
}

// 4. Bib Demo State
const selectedBibFormat = ref<'APA' | 'IEEE' | 'Chicago'>('APA')
const bibFormatOutputs = {
  APA: [
    "Pranata, H. (2025). Analisis Model Transformer untuk Klasifikasi Teks Klinis. Journal of Health Informatics, 12(3), 145-156.",
    "Daniel, M. I. (2026). Penerapan Deep Learning pada Citra Rontgen Paru. Indonesian Medical Journal, 8(1), 12-24."
  ],
  IEEE: [
    'H. Pranata, "Analisis Model Transformer untuk Klasifikasi Teks Klinis," Journal of Health Informatics, vol. 12, no. 3, pp. 145-156, 2025.',
    'M. I. Daniel, "Penerapan Deep Learning pada Citra Rontgen Paru," Indonesian Medical Journal, vol. 8, no. 1, pp. 12-24, 2026.'
  ],
  Chicago: [
    'Pranata, Heru. "Analisis Model Transformer untuk Klasifikasi Teks Klinis." Journal of Health Informatics 12, no. 3 (2025): 145-156.',
    'Daniel, Muhammad Ilham. "Penerapan Deep Learning pada Citra Rontgen Paru." Indonesian Medical Journal 8, no. 1 (2026): 12-24.'
  ]
}
const demoBibCopied = ref(false)
function copyDemoBib() {
  demoBibCopied.value = true
  const text = bibFormatOutputs[selectedBibFormat.value].join('\n\n')
  navigator.clipboard.writeText(text)
  setTimeout(() => { demoBibCopied.value = false }, 2000)
}
</script>

<template>
  <div class="min-h-screen bg-[var(--color-bg)] text-[var(--color-text)] overflow-hidden relative font-sans">
    <!-- Ambient light glows -->
    <div class="absolute -top-40 -left-40 w-[500px] h-[500px] bg-blue-400/10 blur-[130px] rounded-full pointer-events-none animate-float"></div>
    <div class="absolute top-1/3 -right-40 w-[600px] h-[600px] bg-indigo-400/10 blur-[140px] rounded-full pointer-events-none animate-float" style="animation-delay: 2s"></div>
    <div class="absolute -bottom-40 left-1/4 w-[500px] h-[500px] bg-violet-400/80 opacity-[0.03] blur-[150px] rounded-full pointer-events-none"></div>

    <!-- Navbar -->
    <nav class="sticky top-0 z-50 border-b border-[var(--color-border)] bg-[var(--color-surface)]/80 backdrop-blur-md">
      <div class="mx-auto flex max-w-6xl items-center justify-between px-6 py-3.5">
        <div class="flex items-center gap-3">
          <img src="@/assets/logo.png" class="h-11 w-11 object-contain rounded-lg" alt="ResearchFinder Logo" />
          <span class="text-base font-bold tracking-tight bg-gradient-to-r from-zinc-950 to-zinc-700 bg-clip-text text-transparent">ResearchFinder</span>
        </div>
        <div class="flex items-center gap-3">
          <router-link to="/login" class="rounded-md px-3.5 py-1.5 text-xs font-semibold text-[var(--color-text-sub)] transition hover:text-[var(--color-text)]">
            Masuk
          </router-link>
          <button @click="getStarted"
            class="rounded-md bg-[var(--color-primary)] px-4 py-2 text-xs font-bold text-white shadow-sm transition hover:bg-[var(--color-primary-hover)] cursor-pointer">
            Mulai Gratis
          </button>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="relative pt-16 pb-12 overflow-hidden">
      <!-- Subtle dot grid background -->
      <div class="absolute inset-0 opacity-[0.02] pointer-events-none" style="background-image: radial-gradient(circle, #18181b 1.5px, transparent 1.5px); background-size: 30px 30px;"></div>

      <div class="relative mx-auto max-w-4xl px-6 text-center">
        <!-- Badge -->
        <div class="animate-fade-up mb-6 inline-flex items-center gap-2 rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-1.5 text-[11px] font-semibold text-[var(--color-text-sub)] shadow-sm">
          <span class="relative flex h-2 w-2">
            <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-blue-400 opacity-75"></span>
            <span class="relative inline-flex h-2 w-2 rounded-full bg-blue-500"></span>
          </span>
          Didukung AI · 100% Gratis &amp; Open Source untuk Mahasiswa
        </div>

        <!-- Headline -->
        <h1 class="animate-fade-up delay-100 text-4xl font-extrabold leading-[1.15] tracking-tight text-[var(--color-text)] sm:text-5xl lg:text-6xl">
          Temukan &amp; Pahami<br>
          <span class="bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 bg-clip-text text-transparent">Paper Ilmiah</span> Lebih Cepat
        </h1>

        <!-- Subtext -->
        <p class="animate-fade-up delay-200 mx-auto mt-6 max-w-2xl text-sm leading-relaxed text-[var(--color-text-sub)] sm:text-base">
          Platform riset akademik modern untuk membantu mahasiswa menemukan, meringkas, dan menganalisis paper ilmiah dari 
          <span class="text-zinc-950 font-semibold">Semantic Scholar</span> dan <span class="text-zinc-950 font-semibold">arXiv</span> — dilengkapi AI chat asisten, deteksi celah riset, dan bibliografi otomatis.
        </p>

        <!-- CTA -->
        <div class="animate-fade-up delay-300 mt-8 flex flex-wrap items-center justify-center gap-3">
          <button @click="getStarted"
            class="animate-pulse-subtle rounded-md bg-[var(--color-primary)] px-6 py-3 text-xs font-bold text-white shadow-md transition hover:bg-[var(--color-primary-hover)] cursor-pointer">
            Mulai Sekarang — Gratis
          </button>
          <router-link to="/login"
            class="rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-5 py-3 text-xs font-bold text-[var(--color-text-sub)] transition hover:bg-zinc-50 shadow-sm">
            Masuk ke Akun
          </router-link>
        </div>
        <p class="animate-fade-in delay-500 mt-4 text-[11px] text-[var(--color-text-muted)]">Tanpa kartu kredit · Integrasi langsung API akademik</p>
      </div>
    </section>

    <!-- Interactive Product Tour (WOW factor) -->
    <section class="max-w-5xl mx-auto px-6 py-12">
      <div class="reveal mb-8 text-center">
        <h2 class="text-2xl font-bold tracking-tight text-[var(--color-text)]">Uji Fitur AI Secara Langsung</h2>
        <p class="mt-1.5 text-xs text-[var(--color-text-sub)]">Rasakan kecanggihan asisten riset ResearchFinder melalui simulasi interaktif di bawah ini</p>
      </div>

      <!-- Demo Box -->
      <div class="reveal rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-lg overflow-hidden grid grid-cols-1 md:grid-cols-12 min-h-[460px]">
        
        <!-- Left Side: Simulator Tabs -->
        <div class="md:col-span-4 border-r border-[var(--color-border)] bg-zinc-50/50 p-5 flex flex-col justify-between">
          <div class="space-y-2.5">
            <div class="text-[10px] font-bold text-[var(--color-text-muted)] uppercase tracking-wider mb-2">PILIH FITUR UTAMA</div>
            
            <!-- Tab 1 -->
            <button @click="activeDemoTab = 'search'"
              class="w-full text-left p-3 rounded-lg border transition-all duration-300 cursor-pointer flex items-center gap-3"
              :class="activeDemoTab === 'search' ? 'bg-white border-blue-200 shadow-sm text-blue-700 font-semibold' : 'border-transparent text-[var(--color-text-sub)] hover:bg-white/60'">
              <div class="p-1.5 rounded-md" :class="activeDemoTab === 'search' ? 'bg-blue-50 text-blue-600' : 'bg-zinc-100 text-zinc-500'">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>
              </div>
              <div class="text-xs">
                <div>Cari Paper Akademik</div>
                <div class="text-[9px] text-[var(--color-text-muted)] mt-0.5 font-normal">S2 + arXiv Concurrent</div>
              </div>
            </button>

            <!-- Tab 2 -->
            <button @click="activeDemoTab = 'summary'"
              class="w-full text-left p-3 rounded-lg border transition-all duration-300 cursor-pointer flex items-center gap-3"
              :class="activeDemoTab === 'summary' ? 'bg-white border-violet-200 shadow-sm text-violet-700 font-semibold' : 'border-transparent text-[var(--color-text-sub)] hover:bg-white/60'">
              <div class="p-1.5 rounded-md" :class="activeDemoTab === 'summary' ? 'bg-violet-50 text-violet-600' : 'bg-zinc-100 text-zinc-500'">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 3v1m0 16v1m-8-9H3m18 0h-1"/><circle cx="12" cy="12" r="4"/><path d="M17.66 6.34l-.71.71M7.05 16.95l-.71.71m0-12.02l.71.71m9.9 9.9l.71.71"/></svg>
              </div>
              <div class="text-xs">
                <div>Ringkasan AI Pintar</div>
                <div class="text-[9px] text-[var(--color-text-muted)] mt-0.5 font-normal">Key Findings &amp; Metode</div>
              </div>
            </button>

            <!-- Tab 3 -->
            <button @click="activeDemoTab = 'gap'"
              class="w-full text-left p-3 rounded-lg border transition-all duration-300 cursor-pointer flex items-center gap-3"
              :class="activeDemoTab === 'gap' ? 'bg-white border-rose-200 shadow-sm text-rose-700 font-semibold' : 'border-transparent text-[var(--color-text-sub)] hover:bg-white/60'">
              <div class="p-1.5 rounded-md" :class="activeDemoTab === 'gap' ? 'bg-rose-50 text-rose-600' : 'bg-zinc-100 text-zinc-500'">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
              </div>
              <div class="text-xs">
                <div>Research Gap Matrix</div>
                <div class="text-[9px] text-[var(--color-text-muted)] mt-0.5 font-normal">Celah Penelitian 2x2</div>
              </div>
            </button>

            <!-- Tab 4 -->
            <button @click="activeDemoTab = 'bib'"
              class="w-full text-left p-3 rounded-lg border transition-all duration-300 cursor-pointer flex items-center gap-3"
              :class="activeDemoTab === 'bib' ? 'bg-white border-emerald-200 shadow-sm text-emerald-700 font-semibold' : 'border-transparent text-[var(--color-text-sub)] hover:bg-white/60'">
              <div class="p-1.5 rounded-md" :class="activeDemoTab === 'bib' ? 'bg-emerald-50 text-emerald-600' : 'bg-zinc-100 text-zinc-500'">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M4 4.5A2.5 2.5 0 016.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15z"/></svg>
              </div>
              <div class="text-xs">
                <div>Ekspor Sitasi &amp; Bib</div>
                <div class="text-[9px] text-[var(--color-text-muted)] mt-0.5 font-normal">APA / IEEE / Chicago</div>
              </div>
            </button>
          </div>

          <div class="hidden md:block text-[10px] text-[var(--color-text-muted)] border-t border-[var(--color-border)] pt-4">
            💡 Semua data disimulasikan secara lokal agar Anda bisa mencoba dengan instan.
          </div>
        </div>

        <!-- Right Side: Interactive Screen Simulator -->
        <div class="md:col-span-8 p-6 flex flex-col justify-between bg-zinc-950 text-zinc-100 select-none">
          <!-- Terminal Header -->
          <div class="flex items-center justify-between border-b border-zinc-800 pb-3 mb-4">
            <div class="flex items-center gap-2">
              <span class="h-3 w-3 rounded-full bg-rose-500/80"></span>
              <span class="h-3 w-3 rounded-full bg-amber-500/80"></span>
              <span class="h-3 w-3 rounded-full bg-emerald-500/80"></span>
              <span class="ml-2 text-xs font-mono text-zinc-400">Simulator://ResearchFinder/{{ activeDemoTab }}</span>
            </div>
            <span class="text-[10px] bg-zinc-800 text-zinc-300 px-2.5 py-0.5 rounded font-mono uppercase font-bold">LIVE MODE</span>
          </div>

          <!-- Simulator Container -->
          <div class="flex-1 flex flex-col justify-start">
            
            <!-- Content 1: Search Demo -->
            <div v-if="activeDemoTab === 'search'" class="space-y-4">
              <!-- Search Bar Input Simulator -->
              <div class="flex items-center gap-3 rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-2.5">
                <svg width="14" height="14" class="text-zinc-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>
                <input v-model="searchDemoQuery" type="text" readonly class="flex-1 bg-transparent text-xs outline-none text-zinc-100" />
                <span class="text-[10px] text-blue-400 font-bold font-mono">CONCURRENT</span>
              </div>

              <!-- Search Results Cards -->
              <div class="space-y-3">
                <div v-for="(paper, idx) in searchDemoResults" :key="idx"
                  class="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 transition-all duration-300 hover:border-zinc-700">
                  <div class="flex items-start justify-between gap-3">
                    <div class="space-y-1">
                      <div class="flex items-center gap-1.5">
                        <span class="rounded px-1.5 py-0.5 text-[8px] font-bold uppercase tracking-wider"
                          :class="paper.source === 'arxiv' ? 'bg-violet-950 text-violet-300 border border-violet-800/50' : 'bg-blue-950 text-blue-300 border border-blue-800/50'">
                          {{ paper.source === 'arxiv' ? 'arXiv' : 'Semantic Scholar' }}
                        </span>
                        <span class="text-[10px] text-zinc-400 font-medium">{{ paper.year }}</span>
                      </div>
                      <h4 class="text-xs font-semibold text-zinc-100 leading-snug">{{ paper.title }}</h4>
                    </div>
                    <!-- Citations Badge -->
                    <span class="rounded bg-zinc-800 px-2 py-0.5 text-[10px] font-medium text-zinc-300 shrink-0">
                      ↗ {{ paper.cites }} cites
                    </span>
                  </div>

                  <!-- Simulated Action Button -->
                  <div class="mt-3.5 flex items-center justify-between border-t border-zinc-800/60 pt-3">
                    <span class="text-[9px] text-zinc-500 font-mono">ID: temp_paper_{{ idx }}</span>
                    <button @click="toggleSaveDemoPaper(idx)"
                      class="rounded bg-zinc-800 hover:bg-zinc-700 active:scale-95 text-[10px] font-bold text-zinc-100 px-3 py-1 cursor-pointer transition-all">
                      {{ paper.saved ? '✓ Tersimpan di Koleksi' : '+ Simpan ke Koleksi' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Content 2: AI Summarizer Demo -->
            <div v-if="activeDemoTab === 'summary'" class="space-y-3.5">
              <div class="bg-zinc-900/40 border border-zinc-800/80 rounded-lg p-3.5">
                <h4 class="text-xs font-bold text-zinc-100 mb-1">Paper: Deep Learning for Healthcare Applications</h4>
                <p class="text-[10px] text-zinc-400 line-clamp-2 leading-relaxed">
                  Abstract: This study comprehensively reviews the implementation of deep learning algorithms on electronic health records (EHR) to proactively predict chronic diseases...
                </p>
              </div>

              <!-- CTA for Summary -->
              <div class="flex items-center gap-3">
                <button @click="runSummaryDemo" :disabled="isSummarizingDemo"
                  class="rounded bg-violet-600 hover:bg-violet-500 text-xs font-bold px-4 py-2 cursor-pointer transition text-white disabled:opacity-50">
                  {{ isSummarizingDemo ? 'AI sedang meringkas...' : 'Mulai Summarize dengan AI' }}
                </button>
                <span v-if="!summaryDemoResult && !isSummarizingDemo" class="text-[10px] text-zinc-400 animate-pulse">💡 Klik tombol untuk menjalankan generator ringkasan</span>
              </div>

              <!-- Summary Result Output Box -->
              <div v-if="isSummarizingDemo" class="h-28 flex flex-col items-center justify-center gap-2">
                <div class="h-5 w-5 animate-spin rounded-full border-2 border-violet-500 border-t-transparent"></div>
                <span class="text-[10px] text-zinc-400 font-mono">Mengakses Groq LLaMA 3.1 8B...</span>
              </div>

              <div v-else-if="summaryDemoResult" class="rounded-lg border border-violet-900/30 bg-violet-950/10 p-4 space-y-2.5 animate-fade-in text-xs leading-relaxed max-h-56 overflow-y-auto">
                <div>
                  <span class="font-bold text-violet-400">Ringkasan AI:</span>
                  <p class="text-zinc-300 mt-1 text-[11px] leading-relaxed">{{ summaryDemoResult.ringkasan }}</p>
                </div>
                <div>
                  <span class="font-bold text-violet-400">Temuan Utama:</span>
                  <ul class="list-disc pl-4 mt-1 space-y-1 text-zinc-300 text-[11px]">
                    <li v-for="(t, idx) in summaryDemoResult.temuan_utama" :key="idx">{{ t }}</li>
                  </ul>
                </div>
                <div class="border-t border-zinc-800/40 pt-2.5">
                  <span class="font-bold text-violet-400">Metodologi:</span>
                  <span class="text-zinc-300 ml-1.5 text-[11px]">{{ summaryDemoResult.metodologi }}</span>
                </div>
              </div>
            </div>

            <!-- Content 3: Gap Matrix Demo -->
            <div v-if="activeDemoTab === 'gap'" class="space-y-4">
              <div class="text-[10px] text-zinc-400 font-medium">Klik pada salah satu kuadran di bawah ini untuk melihat contoh analisis celah:</div>
              
              <!-- 2x2 Matrix Simulator -->
              <div class="grid grid-cols-2 gap-2">
                <!-- Q1 -->
                <button @click="selectedGapQuadrant = 'q1'"
                  class="rounded-lg border p-3 text-left transition cursor-pointer"
                  :class="selectedGapQuadrant === 'q1' ? 'bg-rose-950/30 border-rose-600 text-rose-400' : 'bg-zinc-900/50 border-zinc-800 text-zinc-400 hover:border-zinc-700'">
                  <div class="text-[10px] font-bold">1. Goldmine (Peluang)</div>
                  <div class="text-[8px] opacity-60 mt-0.5">Prioritas Tinggi · Bahasan Jarang</div>
                </button>
                <!-- Q2 -->
                <button @click="selectedGapQuadrant = 'q2'"
                  class="rounded-lg border p-3 text-left transition cursor-pointer"
                  :class="selectedGapQuadrant === 'q2' ? 'bg-amber-950/30 border-amber-600 text-amber-400' : 'bg-zinc-900/50 border-zinc-800 text-zinc-400 hover:border-zinc-700'">
                  <div class="text-[10px] font-bold">2. Kompetitif (Mainstream)</div>
                  <div class="text-[8px] opacity-60 mt-0.5">Prioritas Tinggi · Bahasan Sering</div>
                </button>
                <!-- Q3 -->
                <button @click="selectedGapQuadrant = 'q3'"
                  class="rounded-lg border p-3 text-left transition cursor-pointer"
                  :class="selectedGapQuadrant === 'q3' ? 'bg-blue-950/30 border-blue-600 text-blue-400' : 'bg-zinc-900/50 border-zinc-800 text-zinc-400 hover:border-zinc-700'">
                  <div class="text-[10px] font-bold">3. Niche (Eksploratif)</div>
                  <div class="text-[8px] opacity-60 mt-0.5">Prioritas Sedang · Bahasan Jarang</div>
                </button>
                <!-- Q4 -->
                <button @click="selectedGapQuadrant = 'q4'"
                  class="rounded-lg border p-3 text-left transition cursor-pointer"
                  :class="selectedGapQuadrant === 'q4' ? 'bg-zinc-800/40 border-zinc-700 text-zinc-300' : 'bg-zinc-900/50 border-zinc-800 text-zinc-400 hover:border-zinc-700'">
                  <div class="text-[10px] font-bold">4. Kolektif (Umum)</div>
                  <div class="text-[8px] opacity-60 mt-0.5">Prioritas Sedang · Bahasan Sering</div>
                </button>
              </div>

              <!-- Quadrant Detail Card -->
              <div class="rounded-lg border border-zinc-800 bg-zinc-900/40 p-4 space-y-1.5 animate-fade-in">
                <div class="flex items-center justify-between">
                  <h5 class="text-xs font-bold text-zinc-100">{{ gapQuadrants[selectedGapQuadrant].title }}</h5>
                  <span class="rounded bg-zinc-800 px-2 py-0.5 text-[9px] font-semibold text-zinc-300">{{ gapQuadrants[selectedGapQuadrant].badge }}</span>
                </div>
                <p class="text-[11px] text-zinc-300 leading-relaxed">{{ gapQuadrants[selectedGapQuadrant].desc }}</p>
              </div>
            </div>

            <!-- Content 4: Bibliography Demo -->
            <div v-if="activeDemoTab === 'bib'" class="space-y-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-1.5">
                  <button @click="selectedBibFormat = 'APA'"
                    class="rounded px-3 py-1 text-[10px] font-bold cursor-pointer transition"
                    :class="selectedBibFormat === 'APA' ? 'bg-emerald-600 text-white' : 'bg-zinc-900 border border-zinc-800 text-zinc-400 hover:bg-zinc-800'">
                    APA Style
                  </button>
                  <button @click="selectedBibFormat = 'IEEE'"
                    class="rounded px-3 py-1 text-[10px] font-bold cursor-pointer transition"
                    :class="selectedBibFormat === 'IEEE' ? 'bg-emerald-600 text-white' : 'bg-zinc-900 border border-zinc-800 text-zinc-400 hover:bg-zinc-800'">
                    IEEE Style
                  </button>
                  <button @click="selectedBibFormat = 'Chicago'"
                    class="rounded px-3 py-1 text-[10px] font-bold cursor-pointer transition"
                    :class="selectedBibFormat === 'Chicago' ? 'bg-emerald-600 text-white' : 'bg-zinc-900 border border-zinc-800 text-zinc-400 hover:bg-zinc-800'">
                    Chicago Style
                  </button>
                </div>
                <button @click="copyDemoBib"
                  class="rounded bg-zinc-800 hover:bg-zinc-700 active:scale-95 text-[10px] font-bold px-3 py-1 cursor-pointer transition-all flex items-center gap-1.5">
                  <svg width="10" height="10" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                  {{ demoBibCopied ? 'Tersalin!' : 'Salin Semua' }}
                </button>
              </div>

              <!-- Output Text Area -->
              <div class="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4 font-mono text-[10px] leading-relaxed space-y-3 max-h-56 overflow-y-auto">
                <div v-for="(entry, index) in bibFormatOutputs[selectedBibFormat]" :key="index" class="text-zinc-300">
                  {{ entry }}
                </div>
              </div>
            </div>

          </div>

          <!-- Simulator Footer -->
          <div class="mt-4 border-t border-zinc-900/60 pt-3 flex items-center justify-between text-[10px] text-zinc-500 font-mono">
            <span>Server: local_node_1 · Response: 12ms</span>
            <span class="text-emerald-500 font-bold">✓ Ready</span>
          </div>
        </div>
        
      </div>
    </section>

    <!-- Features Grid -->
    <section class="max-w-6xl mx-auto px-6 py-16">
      <div class="reveal mb-12 text-center">
        <h2 class="text-2xl font-bold tracking-tight text-[var(--color-text)] sm:text-3xl">Fitur Unggulan Mahasiswa</h2>
        <p class="mt-2 text-sm text-[var(--color-text-sub)]">Dirancang khusus untuk mempermudah pengerjaan Skripsi, Thesis, dan Tugas Akhir</p>
      </div>

      <div class="reveal-stagger grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <!-- Feature 1 -->
        <div class="reveal group rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 transition-all duration-300 hover:border-zinc-300 hover:shadow-md relative overflow-hidden" style="--stagger-index: 0">
          <div class="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
            <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/></svg>
          </div>
          <h3 class="text-sm font-bold text-[var(--color-text)]">Pencarian Multi-Sumber</h3>
          <p class="mt-2 text-xs leading-relaxed text-[var(--color-text-sub)]">
            Cari paper akademik dari Semantic Scholar dan arXiv sekaligus secara real-time. Hilangkan duplikasi hasil secara otomatis untuk menghemat waktu evaluasi Anda.
          </p>
          <div class="mt-4 flex flex-wrap gap-1.5">
            <span class="rounded bg-blue-50 px-2 py-0.5 text-[9px] font-bold text-blue-600">Semantic Scholar</span>
            <span class="rounded bg-violet-50 px-2 py-0.5 text-[9px] font-bold text-violet-600">arXiv</span>
          </div>
        </div>

        <!-- Feature 2 -->
        <div class="reveal group rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 transition-all duration-300 hover:border-zinc-300 hover:shadow-md relative overflow-hidden" style="--stagger-index: 1">
          <div class="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-violet-50 text-violet-600">
            <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M12 3v1m0 16v1m-8-9H3m18 0h-1"/><circle cx="12" cy="12" r="4"/><path d="M17.66 6.34l-.71.71M7.05 16.95l-.71.71m0-12.02l.71.71m9.9 9.9l.71.71"/></svg>
          </div>
          <h3 class="text-sm font-bold text-[var(--color-text)]">AI Paper Summarizer</h3>
          <p class="mt-2 text-xs leading-relaxed text-[var(--color-text-sub)]">
            Dapatkan abstrak dan konten paper yang sudah dirangkum otomatis oleh LLaMA 3.1 ke dalam bahasa Indonesia secara runut, komprehensif, dan mudah dipahami.
          </p>
          <div class="mt-4 flex flex-wrap gap-1.5">
            <span class="rounded bg-violet-50 px-2 py-0.5 text-[9px] font-bold text-violet-600">Groq AI</span>
            <span class="rounded bg-zinc-100 px-2 py-0.5 text-[9px] font-bold text-zinc-600">Bahasa Indonesia</span>
          </div>
        </div>

        <!-- Feature 3 -->
        <div class="reveal group rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 transition-all duration-300 hover:border-zinc-300 hover:shadow-md relative overflow-hidden" style="--stagger-index: 2">
          <div class="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-rose-50 text-rose-600">
            <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
          </div>
          <h3 class="text-sm font-bold text-[var(--color-text)]">Research Gap Analyzer</h3>
          <p class="mt-2 text-xs leading-relaxed text-[var(--color-text-sub)]">
            Bandingkan beberapa paper referensi sekaligus untuk mengidentifikasi celah riset (*research gaps*), metodologi dominan, serta rekomendasi topik lanjutan.
          </p>
          <div class="mt-4 flex flex-wrap gap-1.5">
            <span class="rounded bg-rose-50 px-2 py-0.5 text-[9px] font-bold text-rose-600">Gap Matrix</span>
            <span class="rounded bg-amber-50 px-2 py-0.5 text-[9px] font-bold text-amber-600">Multi-paper Compare</span>
          </div>
        </div>

        <!-- Feature 4 -->
        <div class="reveal group rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 transition-all duration-300 hover:border-zinc-300 hover:shadow-md relative overflow-hidden" style="--stagger-index: 3">
          <div class="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
            <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          </div>
          <h3 class="text-sm font-bold text-[var(--color-text)]">Upload PDF &amp; Metadata Extract</h3>
          <p class="mt-2 text-xs leading-relaxed text-[var(--color-text-sub)]">
            Unggah berkas PDF paper eksternal Anda. AI secara cerdas akan mengekstrak data judul, penulis, tahun, dan abstrak, serta menyimpannya dalam database lokal Anda.
          </p>
          <div class="mt-4 flex flex-wrap gap-1.5">
            <span class="rounded bg-emerald-50 px-2 py-0.5 text-[9px] font-bold text-emerald-600">PyMuPDF Extract</span>
            <span class="rounded bg-zinc-100 px-2 py-0.5 text-[9px] font-bold text-zinc-600">Title Dedup</span>
          </div>
        </div>

        <!-- Feature 5 -->
        <div class="reveal group rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 transition-all duration-300 hover:border-zinc-300 hover:shadow-md relative overflow-hidden" style="--stagger-index: 4">
          <div class="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-sky-50 text-sky-600">
            <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>
          </div>
          <h3 class="text-sm font-bold text-[var(--color-text)]">Translate &amp; Explain</h3>
          <p class="mt-2 text-xs leading-relaxed text-[var(--color-text-sub)]">
            Terjemahkan abstrak bahasa Inggris yang rumit ke bahasa Indonesia akademik formal, atau gunakan fitur "Explain" untuk menerjemahkannya ke bahasa kasual yang mudah dipahami.
          </p>
          <div class="mt-4 flex flex-wrap gap-1.5">
            <span class="rounded bg-sky-50 px-2 py-0.5 text-[9px] font-bold text-sky-600">Explain Text</span>
            <span class="rounded bg-indigo-50 px-2 py-0.5 text-[9px] font-bold text-indigo-600">Clinical/IT Dictionary</span>
          </div>
        </div>

        <!-- Feature 6 -->
        <div class="reveal group rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 transition-all duration-300 hover:border-zinc-300 hover:shadow-md relative overflow-hidden" style="--stagger-index: 5">
          <div class="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
            <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M4 4.5A2.5 2.5 0 016.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15z"/></svg>
          </div>
          <h3 class="text-sm font-bold text-[var(--color-text)]">Koleksi Terstruktur</h3>
          <p class="mt-2 text-xs leading-relaxed text-[var(--color-text-sub)]">
            Kelompokkan paper ke dalam folder-folder koleksi yang rapi. Tambahkan catatan pribadi per paper untuk memudahkan penulisan kajian pustaka skripsi Anda.
          </p>
          <div class="mt-4 flex flex-wrap gap-1.5">
            <span class="rounded bg-indigo-50 px-2 py-0.5 text-[9px] font-bold text-indigo-600">Personal Notes</span>
            <span class="rounded bg-pink-50 px-2 py-0.5 text-[9px] font-bold text-pink-600">Export TXT</span>
          </div>
        </div>
      </div>
    </section>

    <!-- How it works (Cleaned up and modernized) -->
    <section class="border-t border-[var(--color-border)] bg-zinc-50/60 py-16 relative">
      <div class="mx-auto max-w-4xl px-6">
        <div class="reveal mb-12 text-center">
          <h2 class="text-2xl font-bold tracking-tight text-[var(--color-text)] sm:text-3xl">Langkah Praktis Riset</h2>
          <p class="mt-2 text-sm text-[var(--color-text-sub)]">Selesaikan kajian pustaka Anda dalam 3 tahapan sistematis</p>
        </div>

        <div class="reveal-stagger grid gap-8 sm:grid-cols-3">
          <div class="reveal text-center relative" style="--stagger-index: 0">
            <div class="mx-auto mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 text-sm font-bold text-white shadow-md shadow-blue-500/20">1</div>
            <h3 class="text-sm font-bold text-[var(--color-text)]">Cari &amp; Organisasikan</h3>
            <p class="mt-2 text-xs leading-relaxed text-[var(--color-text-sub)]">
              Kumpulkan data riset akademik secara instan melalui pencarian internal atau upload PDF paper fisik milik Anda ke koleksi.
            </p>
          </div>
          <div class="reveal text-center relative" style="--stagger-index: 1">
            <div class="mx-auto mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-violet-600 text-sm font-bold text-white shadow-md shadow-violet-500/20">2</div>
            <h3 class="text-sm font-bold text-[var(--color-text)]">Pahami Cepat via AI</h3>
            <p class="mt-2 text-xs leading-relaxed text-[var(--color-text-sub)]">
              Gunakan Summarizer AI untuk mengekstrak temuan dan metodologi, serta fitur Chat Q&amp;A untuk menanyakan detail metodologi secara asisten pribadi.
            </p>
          </div>
          <div class="reveal text-center relative" style="--stagger-index: 2">
            <div class="mx-auto mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-600 text-sm font-bold text-white shadow-md shadow-emerald-500/20">3</div>
            <h3 class="text-sm font-bold text-[var(--color-text)]">Temukan Celah Riset</h3>
            <p class="mt-2 text-xs leading-relaxed text-[var(--color-text-sub)]">
              Jalankan Gap Analyzer untuk memetakan paper Anda ke dalam Matriks 2x2. Temukan celah riset yang siap menjadi topik skripsi baru Anda.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Tech stack badges -->
    <section class="max-w-4xl mx-auto px-6 py-16">
      <div class="reveal mb-8 text-center">
        <h2 class="text-base font-bold text-[var(--color-text-sub)] uppercase tracking-wider">TEKNOLOGI KELAS AKADEMIK</h2>
      </div>
      <div class="reveal flex flex-wrap items-center justify-center gap-2 max-w-2xl mx-auto">
        <span v-for="tech in ['Vue 3', 'TypeScript', 'FastAPI', 'Tailwind CSS v4', 'Groq LLaMA 3', 'Semantic Scholar API', 'arXiv API', 'PyMuPDF', 'SQLAlchemy', 'PostgreSQL', 'Docker']"
          :key="tech"
          class="rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-1.5 text-xs font-semibold text-[var(--color-text-sub)] shadow-sm transition-all duration-300 hover:border-zinc-400 hover:text-[var(--color-text)]">
          {{ tech }}
        </span>
      </div>
    </section>

    <!-- CTA bottom (Premium Banner) -->
    <section class="border-t border-[var(--color-border)] bg-gradient-to-b from-[var(--color-surface)] to-zinc-50 py-20 relative overflow-hidden">
      <div class="absolute inset-0 bg-grid-pattern opacity-[0.01]"></div>
      <div class="reveal mx-auto max-w-2xl px-6 text-center relative z-10 space-y-6">
        <h2 class="text-3xl font-extrabold tracking-tight text-[var(--color-text)] sm:text-4xl">Siap Mempercepat Riset Skripsi Anda?</h2>
        <p class="text-sm leading-relaxed text-[var(--color-text-sub)] max-w-md mx-auto">
          Bergabung sekarang bersama mahasiswa Indonesia lainnya dan temukan kemudahan menyusun kajian pustaka dengan kecerdasan AI.
        </p>
        <div class="pt-2">
          <button @click="getStarted"
            class="rounded-md bg-[var(--color-primary)] px-7 py-3 text-xs font-extrabold text-white shadow-lg shadow-blue-500/20 transition hover:bg-[var(--color-primary-hover)] cursor-pointer">
            Mulai Registrasi Akun — Gratis
          </button>
        </div>
        <p class="text-[10px] text-[var(--color-text-muted)]">Open source · Bebas iklan · Privasi dokumen terjamin</p>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-[var(--color-border)] bg-[var(--color-surface)] py-8 relative z-10">
      <div class="mx-auto max-w-6xl px-6 flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
        <div class="flex items-center gap-2.5">
          <img src="@/assets/logo.png" class="h-10 w-10 object-contain rounded-lg" alt="ResearchFinder Logo" />
          <span class="text-base font-bold text-[var(--color-text)]">ResearchFinder</span>
        </div>
        <div class="text-center sm:text-right space-y-1">
          <p class="text-[11px] text-[var(--color-text-muted)]">
            © 2026 ResearchFinder · Dibuat untuk mempercepat riset mahasiswa Indonesia
          </p>
          <div class="text-[10px] text-[var(--color-text-muted)]">
            Didukung oleh Semantic Scholar &amp; arXiv API data.
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>
