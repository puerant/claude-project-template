import { client } from './client'
import type { Task, TaskStatus } from '../types'

export const getTasks = (projectId: string, status?: TaskStatus) =>
  client.get<Task[]>(`/projects/${projectId}/tasks`, { params: status ? { status } : {} }).then(r => r.data)

export const getTask = (taskId: string) =>
  client.get<Task>(`/tasks/${taskId}`).then(r => r.data)

export const executeTask = (taskId: string) =>
  client.post(`/tasks/${taskId}/execute`).then(r => r.data)

export const cancelTask = (taskId: string) =>
  client.post(`/tasks/${taskId}/cancel`).then(r => r.data)

export const resetTask = (taskId: string) =>
  client.post(`/tasks/${taskId}/reset`).then(r => r.data)

export const reviewTask = (taskId: string, result: 'pass' | 'fail', failedCriteria: string[] = []) =>
  client.post(`/tasks/${taskId}/review`, { result, failedCriteria }).then(r => r.data)
