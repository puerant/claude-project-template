import { ref } from 'vue'
import { getBugReports } from '../api/bugs'
import type { BugReport } from '../types'

export function useBugList(projectId: string) {
  const bugs = ref<BugReport[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchBugs() {
    loading.value = true
    error.value = null
    try {
      bugs.value = await getBugReports(projectId)
    } catch {
      error.value = '加载 Bug 报告失败'
    } finally {
      loading.value = false
    }
  }

  return { bugs, loading, error, fetchBugs }
}
