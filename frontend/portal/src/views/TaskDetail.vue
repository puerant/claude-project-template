<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold text-gray-800">任务详情</h1>
    <p class="text-gray-400 mt-2">任务 ID：{{ route.params.taskId }}</p>
  </div>
</template>
