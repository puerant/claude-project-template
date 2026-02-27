import { client } from './client'
import type { BugReport } from '../types'

export const getBugReports = (projectId: string) =>
  client.get<BugReport[]>(`/projects/${projectId}/bugs`).then(r => r.data)
