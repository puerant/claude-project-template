<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold text-gray-800">Bug 报告列表</h1>
    <p class="text-gray-400 mt-2">项目 ID：{{ route.params.id }}</p>
  </div>
</template>
