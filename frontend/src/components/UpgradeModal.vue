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
              :disabled="loading"
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
              @click="payWithMidtrans"
              :disabled="loading"
              class="mt-5 w-full py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-bold text-sm rounded-xl transition shadow-lg shadow-amber-500/20 cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <span>{{ loading ? 'Membuka Midtrans Gateway...' : 'Bayar via Midtrans (Rp 29.000)' }}</span>
              <span v-if="!loading">→</span>
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
const loading = ref(false)

async function payWithMidtrans() {
  loading.value = true
  try {
    const { data } = await api.post('/payment/create-midtrans-snap')
    
    if (data.auto_upgraded) {
      await refreshUserStatus()
      alert('🎉 Selamat! Akun Anda telah berhasil di-upgrade ke Paket Pro Student (Kuota 5 GB)!')
      return
    }

    const token = data.token
    if (window.snap && token) {
      window.snap.pay(token, {
        onSuccess: async function () {
          await refreshUserStatus()
        },
        onPending: function () {
          alert('Pembayaran Anda sedang diproses. Silakan selesaikan pembayaran di Midtrans.')
        },
        onError: function () {
          alert('Pembayaran gagal atau dibatalkan.')
        },
        onClose: function () {
          console.log('Midtrans Snap popup closed')
        }
      })
    } else if (data.redirect_url) {
      window.open(data.redirect_url, '_blank')
    }
  } catch (err) {
    console.error('Failed to launch Midtrans:', err)
    alert('Gagal membuka Midtrans Gateway. Silakan coba lagi.')
  } finally {
    loading.value = false
  }
}

async function refreshUserStatus() {
  try {
    const { data } = await api.get('/auth/me')
    authStore.user = data
    emit('upgraded')
    emit('close')
    alert('🎉 Terima Kasih! Pembayaran Midtrans Anda telah berhasil! Akun Anda kini resmi aktif di Paket Pro Student (Kuota 5 GB)!')
  } catch (err) {
    console.error('Failed to refresh status:', err)
  }
}

async function handleDowngrade() {
  loading.value = true
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
    loading.value = false
  }
}
</script>
