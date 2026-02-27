import { client } from './client'
import type { Project, SyncResult } from '../types'

export const getProjects = () =>
  client.get<Project[]>('/projects').then(r => r.data)

export const createProject = (name: string, path: string) =>
  client.post<Project>('/projects', { name, path }).then(r => r.data)

export const deleteProject = (id: string) =>
  client.delete(`/projects/${id}`)

export const syncProject = (id: string) =>
  client.post<SyncResult>(`/projects/${id}/sync`).then(r => r.data)
