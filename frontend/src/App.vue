<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import { computed } from 'vue'
import AppSidebar from '@/components/ui/AppSidebar.vue'

const route = useRoute()
const isAuthPage = computed(() => route.meta.hideSidebar === true)
</script>

<template>
  <div class="flex min-h-screen bg-[var(--color-bg)]">
    <AppSidebar v-if="!isAuthPage" />
    <main
      class="flex-1 min-h-screen"
      :class="{ 'ml-[252px]': !isAuthPage }"
    >
      <RouterView />
    </main>
  </div>
</template>
