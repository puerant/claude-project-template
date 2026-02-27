import { client } from './client'
import type { LogEntry } from '../types'

export const getLogs = (taskId: string) =>
  client.get<LogEntry[]>(`/tasks/${taskId}/logs`).then(r => r.data)

export const getLogStreamUrl = (taskId: string) =>
  `/api/tasks/${taskId}/logs/stream`
