import { ref, onUnmounted } from 'vue'
import { getLogs, getLogStreamUrl } from '../api/logs'
import { getTask } from '../api/tasks'
import type { LogEntry, Task } from '../types'

export function useLogView(taskId: string) {
  const logs = ref<LogEntry[]>([])
  const task = ref<Task | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const streaming = ref(false)
  const autoScroll = ref(true)

  let es: EventSource | null = null

  async function init() {
    loading.value = true
    error.value = null
    try {
      const [logData, taskData] = await Promise.all([getLogs(taskId), getTask(taskId)])
      logs.value = logData
      task.value = taskData
      if (taskData.status === 'in_progress') {
        startStream()
      }
    } catch {
      error.value = '加载日志失败'
    } finally {
      loading.value = false
    }
  }

  function startStream() {
    if (es) return
    streaming.value = true
    es = new EventSource(getLogStreamUrl(taskId))

    es.addEventListener('log', (e: MessageEvent) => {
      try {
        const entry: LogEntry = JSON.parse(e.data)
        logs.value.push(entry)
      } catch { /* ignore malformed */ }
    })

    es.addEventListener('done', () => {
      stopStream()
    })

    es.addEventListener('error', () => {
      stopStream()
      error.value = 'SSE 连接异常'
    })
  }

  function stopStream() {
    streaming.value = false
    if (es) {
      es.close()
      es = null
    }
  }

  onUnmounted(stopStream)

  return { logs, task, loading, error, streaming, autoScroll, init }
}
