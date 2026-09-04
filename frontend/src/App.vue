<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import { computed } from 'vue'
import AppSidebar from '@/components/ui/AppSidebar.vue'

const route = useRoute()
const showSidebar = computed(() => {
  return !!route.name && !route.meta.hideSidebar
})
</script>

<template>
  <div class="flex min-h-screen bg-[var(--color-bg)]">
    <AppSidebar v-if="showSidebar" />
    <main
      class="flex-1 min-h-screen"
      :class="{ 'ml-[252px]': showSidebar }"
    >
      <RouterView />
    </main>
  </div>
</template>
