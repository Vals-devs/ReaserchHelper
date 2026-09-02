<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div class="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-2xl w-full overflow-hidden shadow-2xl relative animate-scale-up">
        <!-- Close Button -->
        <button
          @click="$emit('close')"
          class="absolute top-4 right-4 text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800 transition z-10 cursor-pointer"
        >
          ✕
        </button>

        <!-- STEP 1: PLAN COMPARISON -->
        <div v-if="step === 'select'">
          <!-- Header Banner -->
          <div class="bg-gradient-to-r from-amber-500/20 via-indigo-500/20 to-blue-500/20 p-6 border-b border-slate-800 text-center relative overflow-hidden">
            <div class="inline-flex p-3 bg-amber-500/20 rounded-2xl mb-3 border border-amber-500/30">
              <!-- Crown Vector Icon -->
              <svg class="w-8 h-8 text-amber-400 fill-amber-400" viewBox="0 0 24 24">
                <path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5zm14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"/>
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-white mb-1">Upgrade ke ResearchFinder Pro</h2>
            <p class="text-slate-300 text-sm max-w-md mx-auto">
              Buka seluruh potensi riset & skripsi Anda tanpa batasan penyimpanan dan AI tingkat lanjut.
            </p>
          </div>

          <!-- Feature Comparison Grid -->
          <div class="p-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <!-- Free Plan -->
            <div class="bg-slate-800/40 rounded-xl p-5 border border-slate-700/50 flex flex-col justify-between">
              <div>
                <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Paket Gratis</span>
                <div class="text-2xl font-extrabold text-white my-2">Rp 0 <span class="text-xs font-normal text-slate-400">/ selamanya</span></div>
                <ul class="space-y-2.5 text-xs text-slate-300 mt-4">
                  <li class="flex items-center gap-2">
                    <span class="text-slate-500 font-bold">✓</span> Kuota Storage PDF 100 MB (~15 Dokumen)
                  </li>
                  <li class="flex items-center gap-2">
                    <span class="text-slate-500 font-bold">✓</span> Max 10 MB per File PDF
                  </li>
                  <li class="flex items-center gap-2">
                    <span class="text-slate-500 font-bold">✓</span> Max 3 Paper di AI Gap Analysis
                  </li>
                  <li class="flex items-center gap-2">
                    <span class="text-slate-500 font-bold">✓</span> Ekspor Sitasi Format APA & IEEE
                  </li>
                </ul>
              </div>
              <button
                v-if="authStore.user?.plan_tier === 'pro'"
                @click="handleDowngrade"
                :disabled="upgrading"
                class="mt-5 w-full py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 font-semibold text-xs rounded-xl transition cursor-pointer"
              >
                Kembali ke Paket Gratis (100 MB)
              </button>
            </div>

            <!-- Pro Plan -->
            <div class="bg-gradient-to-b from-amber-500/10 to-slate-800/60 rounded-xl p-5 border-2 border-amber-500/50 flex flex-col justify-between relative shadow-xl shadow-amber-500/5">
              <div class="absolute -top-3 right-4 bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 font-extrabold text-[10px] uppercase px-2.5 py-0.5 rounded-full shadow">
                Paling Populer
              </div>
              <div>
                <span class="text-xs font-semibold uppercase tracking-wider text-amber-400">Pro Student Plan</span>
                <div class="text-2xl font-extrabold text-amber-300 my-2">Rp 29.000 <span class="text-xs font-normal text-slate-400">/ bulan</span></div>
                <ul class="space-y-2.5 text-xs text-slate-200 mt-4">
                  <li class="flex items-center gap-2">
                    <span class="text-amber-400 font-bold">✓</span> <strong>Kuota Storage PDF 5 GB</strong> (1000+ Dokumen)
                  </li>
                  <li class="flex items-center gap-2">
                    <span class="text-amber-400 font-bold">✓</span> <strong>Max 50 MB per File PDF</strong> (Tanpa Batas Halaman)
                  </li>
                  <li class="flex items-center gap-2">
                    <span class="text-amber-400 font-bold">✓</span> <strong>Max 15 Paper di AI Gap Analysis</strong> Matrix
                  </li>
                  <li class="flex items-center gap-2">
                    <span class="text-amber-400 font-bold">✓</span> <strong>Ekspor ke Mendeley, EndNote (.BIB) & BibTeX</strong>
                  </li>
                  <li class="flex items-center gap-2">
                    <span class="text-amber-400 font-bold">✓</span> <strong>Prioritas AI Fast Reasoning</strong> Response
                  </li>
                </ul>
              </div>

              <button
                @click="step = 'payment'"
                class="mt-5 w-full py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-bold text-sm rounded-xl transition shadow-lg shadow-amber-500/20 cursor-pointer flex items-center justify-center gap-2"
              >
                <span>Pilih Metode Pembayaran</span>
                <span>→</span>
              </button>
            </div>
          </div>
        </div>

        <!-- STEP 2: SELECT PAYMENT METHOD -->
        <div v-else-if="step === 'payment'" class="p-6">
          <div class="flex items-center gap-3 pb-4 mb-4 border-b border-slate-800">
            <button @click="step = 'select'" class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition">
              ← Kembali
            </button>
            <div>
              <h3 class="text-lg font-bold text-white">Pilih Metode Pembayaran</h3>
              <p class="text-xs text-slate-400">Total Tagihan: <strong class="text-amber-400">Rp 29.000 / bulan</strong></p>
            </div>
          </div>

          <div class="space-y-3 mb-6">
            <!-- QRIS Option -->
            <label
              @click="selectedMethod = 'qris'; step = 'confirm'"
              class="flex items-center justify-between p-4 rounded-xl border border-slate-700/80 bg-slate-800/50 hover:border-amber-500/80 hover:bg-slate-800 transition cursor-pointer group"
            >
              <div class="flex items-center gap-3">
                <div class="p-2.5 bg-slate-700/60 rounded-lg group-hover:bg-amber-500/20 transition text-amber-400">
                  <!-- Smartphone Vector Icon -->
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <rect x="5" y="2" width="14" height="20" rx="2" ry="2"/>
                    <line x1="12" y1="18" x2="12.01" y2="18"/>
                  </svg>
                </div>
                <div>
                  <div class="text-sm font-semibold text-white">QRIS (GoPay, OVO, DANA, ShopeePay, Mobile Banking)</div>
                  <div class="text-xs text-slate-400">Scan kode QR instant tanpa biaya admin</div>
                </div>
              </div>
              <span class="text-amber-400 text-sm font-semibold group-hover:translate-x-1 transition">Pilih →</span>
            </label>

            <!-- BCA VA Option -->
            <label
              @click="selectedMethod = 'bca'; step = 'confirm'"
              class="flex items-center justify-between p-4 rounded-xl border border-slate-700/80 bg-slate-800/50 hover:border-amber-500/80 hover:bg-slate-800 transition cursor-pointer group"
            >
              <div class="flex items-center gap-3">
                <div class="p-2 bg-blue-500/10 rounded-lg group-hover:bg-amber-500/20 transition text-blue-400 font-bold text-xs">
                  BCA
                </div>
                <div>
                  <div class="text-sm font-semibold text-white">BCA Virtual Account</div>
                  <div class="text-xs text-slate-400">Transfer via m-BCA / KlikBCA / ATM BCA</div>
                </div>
              </div>
              <span class="text-amber-400 text-sm font-semibold group-hover:translate-x-1 transition">Pilih →</span>
            </label>

            <!-- Mandiri VA Option -->
            <label
              @click="selectedMethod = 'mandiri'; step = 'confirm'"
              class="flex items-center justify-between p-4 rounded-xl border border-slate-700/80 bg-slate-800/50 hover:border-amber-500/80 hover:bg-slate-800 transition cursor-pointer group"
            >
              <div class="flex items-center gap-3">
                <div class="p-2 bg-yellow-500/10 rounded-lg group-hover:bg-amber-500/20 transition text-yellow-400 font-bold text-xs">
                  MDR
                </div>
                <div>
                  <div class="text-sm font-semibold text-white">Mandiri Virtual Account</div>
                  <div class="text-xs text-slate-400">Transfer via Livin' by Mandiri / ATM</div>
                </div>
              </div>
              <span class="text-amber-400 text-sm font-semibold group-hover:translate-x-1 transition">Pilih →</span>
            </label>
          </div>
        </div>

        <!-- STEP 3: INVOICE & SIMULATE PAYMENT -->
        <div v-else-if="step === 'confirm'" class="p-6">
          <div class="flex items-center gap-3 pb-4 mb-4 border-b border-slate-800">
            <button @click="step = 'payment'" class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition">
              ← Ganti Metode
            </button>
            <div>
              <h3 class="text-lg font-bold text-white">Konfirmasi Pembayaran</h3>
              <p class="text-xs text-slate-400">Simulasi Payment Gateway ResearchFinder</p>
            </div>
          </div>

          <!-- Invoice Details -->
          <div class="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 mb-6">
            <div class="flex justify-between items-center text-sm border-b border-slate-700/60 pb-3 mb-3">
              <span class="text-slate-400">Produk:</span>
              <span class="font-bold text-white">ResearchFinder Pro Student Plan (1 Bulan)</span>
            </div>
            <div class="flex justify-between items-center text-sm border-b border-slate-700/60 pb-3 mb-3">
              <span class="text-slate-400">Metode Pembayaran:</span>
              <span class="font-semibold text-amber-400 uppercase">{{ selectedMethod }}</span>
            </div>
            <div class="flex justify-between items-center text-sm">
              <span class="text-slate-400">Total Tagihan:</span>
              <span class="text-xl font-extrabold text-amber-300">Rp 29.000</span>
            </div>
          </div>

          <!-- QR Code Preview if QRIS -->
          <div v-if="selectedMethod === 'qris'" class="text-center bg-white p-4 rounded-xl max-w-[200px] mx-auto mb-6 shadow-lg">
            <div class="w-36 h-36 mx-auto bg-slate-900 p-2 rounded-lg flex items-center justify-center text-white font-mono text-xs text-center border-4 border-amber-500">
              [ QRIS KODE SIMULASI ]
            </div>
            <p class="text-[10px] text-slate-600 font-semibold mt-2">Scan dengan E-Wallet / M-Banking</p>
          </div>

          <!-- VA Number Preview if VA -->
          <div v-else class="bg-slate-800/80 p-4 rounded-xl text-center mb-6 border border-amber-500/30">
            <div class="text-xs text-slate-400 mb-1">Nomor Virtual Account {{ selectedMethod.toUpperCase() }}:</div>
            <div class="text-2xl font-mono font-bold text-amber-300 tracking-wider">880129384910283</div>
            <div class="text-[10px] text-slate-400 mt-1">Berlaku selama 24 jam</div>
          </div>

          <div class="flex gap-3">
            <button
              @click="step = 'select'"
              class="w-1/2 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-sm rounded-xl transition cursor-pointer"
            >
              Batal
            </button>
            <button
              @click="handleUpgrade"
              :disabled="upgrading"
              class="w-1/2 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-bold text-sm rounded-xl transition shadow-lg shadow-amber-500/20 disabled:opacity-50 cursor-pointer"
            >
              {{ upgrading ? 'Verifikasi Pembayaran...' : 'Konfirmasi & Bayar (Rp 29.000)' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const emit = defineEmits(['close', 'upgraded'])
const authStore = useAuthStore()
const step = ref<'select' | 'payment' | 'confirm'>('select')
const selectedMethod = ref('qris')
const upgrading = ref(false)

async function handleUpgrade() {
  upgrading.value = true
  try {
    const { data } = await api.post('/auth/upgrade-pro')
    authStore.user = data
    emit('upgraded')
    emit('close')
    alert('Pembayaran Berhasil! Akun Anda telah resmi di-upgrade ke Paket Pro Student (Kuota 5 GB)!')
  } catch (err) {
    console.error('Failed to upgrade:', err)
    alert('Gagal memproses upgrade. Silakan coba lagi.')
  } finally {
    upgrading.value = false
  }
}

async function handleDowngrade() {
  upgrading.value = true
  try {
    const { data } = await api.post('/auth/downgrade-free')
    authStore.user = data
    emit('upgraded')
    emit('close')
    alert('Akun Anda telah dikembalikan ke Paket Gratis (Kuota 100 MB).')
  } catch (err) {
    console.error('Failed to downgrade:', err)
    alert('Gagal memproses downgrade.')
  } finally {
    upgrading.value = false
  }
}
</script>
