import { ref } from 'vue'
import {
  getTask,
  executeTask as apiExecute,
  cancelTask as apiCancel,
  resetTask as apiReset,
  reviewTask as apiReview,
} from '../api/tasks'
import type { Task } from '../types'

export function useTaskDetail(taskId: string) {
  const task = ref<Task | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const operating = ref(false)

  async function fetchTask() {
    loading.value = true
    error.value = null
    try {
      task.value = await getTask(taskId)
    } catch {
      error.value = '获取任务详情失败'
    } finally {
      loading.value = false
    }
  }

  async function execute() {
    operating.value = true
    try {
      await apiExecute(taskId)
      await fetchTask()
    } catch {
      error.value = '触发执行失败'
    } finally {
      operating.value = false
    }
  }

  async function cancel() {
    operating.value = true
    try {
      await apiCancel(taskId)
      await fetchTask()
    } catch {
      error.value = '取消失败'
    } finally {
      operating.value = false
    }
  }

  async function reset() {
    operating.value = true
    try {
      await apiReset(taskId)
      await fetchTask()
    } catch {
      error.value = '重置失败'
    } finally {
      operating.value = false
    }
  }

  async function review(result: 'pass' | 'fail', failedCriteria: string[] = []) {
    operating.value = true
    try {
      await apiReview(taskId, result, failedCriteria)
      await fetchTask()
    } catch {
      error.value = 'review 提交失败'
    } finally {
      operating.value = false
    }
  }

  return { task, loading, error, operating, fetchTask, execute, cancel, reset, review }
}
