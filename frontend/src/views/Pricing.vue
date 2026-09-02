<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12 animate-fade-in">
    <!-- Header -->
    <div class="max-w-4xl mx-auto text-center mb-12">
      <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold uppercase tracking-wider mb-4">
        <!-- Crown Vector Icon -->
        <svg class="w-4 h-4 text-amber-400 fill-amber-400" viewBox="0 0 24 24">
          <path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5zm14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"/>
        </svg>
        <span>Pilihan Paket Membership</span>
      </div>
      <h1 class="text-3xl md:text-5xl font-extrabold text-white mb-4">
        Tingkatkan Efisiensi Riset & Skripsi Anda
      </h1>
      <p class="text-slate-400 text-base md:text-lg max-w-2xl mx-auto">
        Pilih paket yang paling sesuai dengan kebutuhan akademis Anda. Bebas upgrade atau batalkan kapan saja.
      </p>
    </div>

    <!-- Pricing Cards Grid -->
    <div class="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Free Plan Card -->
      <div class="bg-slate-900/60 border border-slate-800 rounded-3xl p-8 flex flex-col justify-between hover:border-slate-700 transition">
        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Paket Gratis</span>
          <div class="text-4xl font-extrabold text-white my-4">
            Rp 0 <span class="text-sm font-normal text-slate-400">/ selamanya</span>
          </div>
          <p class="text-xs text-slate-400 mb-6">Cocok untuk pencarian paper dasar dan eksplorasi topik awal.</p>

          <div class="border-t border-slate-800 pt-6">
            <ul class="space-y-3.5 text-sm text-slate-300">
              <li class="flex items-center gap-3">
                <span class="text-slate-500 font-bold">✓</span> Kuota Storage PDF 100 MB (~15 Dokumen)
              </li>
              <li class="flex items-center gap-3">
                <span class="text-slate-500 font-bold">✓</span> Max 10 MB per File PDF
              </li>
              <li class="flex items-center gap-3">
                <span class="text-slate-500 font-bold">✓</span> Max 3 Paper di AI Gap Analysis
              </li>
              <li class="flex items-center gap-3">
                <span class="text-slate-500 font-bold">✓</span> Ekspor Sitasi Format APA & IEEE
              </li>
            </ul>
          </div>
        </div>

        <button
          v-if="authStore.user?.plan_tier === 'pro'"
          @click="handleDowngrade"
          :disabled="upgrading"
          class="mt-8 w-full py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-xl text-sm transition cursor-pointer"
        >
          Kembali ke Paket Gratis (100 MB)
        </button>
        <button
          v-else
          disabled
          class="mt-8 w-full py-3 bg-slate-800 text-slate-400 font-semibold rounded-xl text-sm opacity-60"
        >
          Paket Saat Ini
        </button>
      </div>

      <!-- Pro Plan Card -->
      <div class="bg-gradient-to-b from-amber-500/10 via-slate-900/90 to-slate-900 border-2 border-amber-500/60 rounded-3xl p-8 flex flex-col justify-between relative shadow-2xl shadow-amber-500/10 hover:border-amber-400 transition">
        <div class="absolute -top-4 right-8 bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 font-black text-xs uppercase px-4 py-1 rounded-full shadow-lg">
          Paling Populer
        </div>

        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-amber-400">Pro Student Plan</span>
          <div class="text-4xl font-extrabold text-amber-300 my-4">
            Rp 29.000 <span class="text-sm font-normal text-slate-400">/ bulan</span>
          </div>
          <p class="text-xs text-amber-200/80 mb-6">Dirancang khusus untuk mahasiswa skripsi/tesis & peneliti aktif.</p>

          <div class="border-t border-amber-500/20 pt-6">
            <ul class="space-y-3.5 text-sm text-slate-200">
              <li class="flex items-center gap-3">
                <span class="text-amber-400 font-bold text-base">✓</span> <strong>Kuota Storage PDF 5 GB</strong> (1000+ Dokumen)
              </li>
              <li class="flex items-center gap-3">
                <span class="text-amber-400 font-bold text-base">✓</span> <strong>Max 50 MB per File PDF</strong> (Tanpa Batas Halaman)
              </li>
              <li class="flex items-center gap-3">
                <span class="text-amber-400 font-bold text-base">✓</span> <strong>Max 15 Paper di AI Gap Analysis</strong> Matrix
              </li>
              <li class="flex items-center gap-3">
                <span class="text-amber-400 font-bold text-base">✓</span> <strong>Ekspor ke Mendeley, EndNote (.BIB) & BibTeX</strong>
              </li>
              <li class="flex items-center gap-3">
                <span class="text-amber-400 font-bold text-base">✓</span> <strong>Prioritas AI Fast Reasoning</strong> Response
              </li>
            </ul>
          </div>
        </div>

        <button
          @click="showModal = true"
          class="mt-8 w-full py-3.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-extrabold rounded-xl text-sm transition shadow-lg shadow-amber-500/25 cursor-pointer flex items-center justify-center gap-2"
        >
          <span>{{ authStore.user?.plan_tier === 'pro' ? 'Akun Anda Saat Ini (Pro)' : 'Pilih Metode Pembayaran (Rp 29.000/bln)' }}</span>
          <span>→</span>
        </button>
      </div>
    </div>

    <!-- Upgrade Modal -->
    <UpgradeModal v-if="showModal" @close="showModal = false" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import UpgradeModal from '@/components/UpgradeModal.vue'

const authStore = useAuthStore()
const upgrading = ref(false)
const showModal = ref(false)

async function handleDowngrade() {
  upgrading.value = true
  try {
    const { data } = await api.post('/auth/downgrade-free')
    authStore.user = data
    alert('Akun Anda telah dikembalikan ke Paket Gratis (Kuota 100 MB).')
  } catch (err) {
    console.error('Failed to downgrade:', err)
    alert('Gagal memproses downgrade.')
  } finally {
    upgrading.value = false
  }
}
</script>
