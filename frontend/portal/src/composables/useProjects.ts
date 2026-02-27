import { ref } from 'vue'
import { getProjects, createProject, deleteProject, syncProject } from '../api/projects'
import type { Project, SyncResult } from '../types'

export function useProjects() {
  const projects = ref<Project[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchProjects() {
    loading.value = true
    error.value = null
    try {
      projects.value = await getProjects()
    } catch (e) {
      error.value = '获取项目列表失败'
    } finally {
      loading.value = false
    }
  }

  async function addProject(name: string, path: string): Promise<Project | null> {
    try {
      const project = await createProject(name, path)
      projects.value.push(project)
      return project
    } catch (e) {
      error.value = '新增项目失败'
      return null
    }
  }

  async function removeProject(id: string): Promise<boolean> {
    try {
      await deleteProject(id)
      projects.value = projects.value.filter(p => p.id !== id)
      return true
    } catch (e) {
      error.value = '删除项目失败'
      return false
    }
  }

  async function sync(id: string): Promise<SyncResult | null> {
    try {
      return await syncProject(id)
    } catch (e) {
      error.value = '同步项目失败'
      return null
    }
  }

  return { projects, loading, error, fetchProjects, addProject, removeProject, sync }
}
