<script setup lang="ts">
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-6">
      <RouterLink to="/" class="font-semibold text-gray-800 hover:text-blue-600 transition-colors">
        Claude Code Manager
      </RouterLink>
    </nav>
    <main class="container mx-auto px-6 py-8 max-w-7xl">
      <RouterView />
    </main>
  </div>
</template>
