import { ref, computed } from 'vue'
import {
  getTasks,
  executeTask as apiExecute,
  cancelTask as apiCancel,
  resetTask as apiReset,
  reviewTask as apiReview,
} from '../api/tasks'
import type { Task, TaskStatus } from '../types'

const COLUMN_ORDER: TaskStatus[] = [
  'pending', 'in_progress', 'pending_review', 'completed', 'failed', 'cancelled',
]

export function useTaskBoard(projectId: string) {
  const tasks = ref<Task[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const operating = ref<Record<string, boolean>>({})

  const columns = computed(() =>
    COLUMN_ORDER.map(status => ({
      status,
      tasks: tasks.value.filter(t => t.status === status),
    }))
  )

  async function fetchTasks() {
    loading.value = true
    error.value = null
    try {
      tasks.value = await getTasks(projectId)
    } catch {
      error.value = '获取任务列表失败'
    } finally {
      loading.value = false
    }
  }

  async function execute(taskId: string) {
    operating.value[taskId] = true
    try {
      await apiExecute(taskId)
      await fetchTasks()
    } catch {
      error.value = '触发执行失败'
    } finally {
      operating.value[taskId] = false
    }
  }

  async function cancel(taskId: string) {
    operating.value[taskId] = true
    try {
      await apiCancel(taskId)
      await fetchTasks()
    } catch {
      error.value = '取消失败'
    } finally {
      operating.value[taskId] = false
    }
  }

  async function reset(taskId: string) {
    operating.value[taskId] = true
    try {
      await apiReset(taskId)
      await fetchTasks()
    } catch {
      error.value = '重置失败'
    } finally {
      operating.value[taskId] = false
    }
  }

  async function review(taskId: string, result: 'pass' | 'fail', failedCriteria: string[] = []) {
    operating.value[taskId] = true
    try {
      await apiReview(taskId, result, failedCriteria)
      await fetchTasks()
    } catch {
      error.value = 'review 提交失败'
    } finally {
      operating.value[taskId] = false
    }
  }

  return { tasks, columns, loading, error, operating, fetchTasks, execute, cancel, reset, review }
}
