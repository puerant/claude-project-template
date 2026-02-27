// 通用响应包装
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

// 枚举类型
export type TaskStatus = 'pending' | 'in_progress' | 'pending_review' | 'completed' | 'failed' | 'cancelled'
export type TaskType = 'feature' | 'bug'
export type LogStream = 'stdout' | 'stderr'

// 任务统计
export interface TaskStats {
  total: number
  pending: number
  in_progress: number
  pending_review: number
  completed: number
  failed: number
  cancelled: number
}

// 项目
export interface Project {
  id: string
  name: string
  path: string
  createdAt: string
  taskStats: TaskStats
}

// 任务
export interface Task {
  id: string
  projectId: string
  type: TaskType
  title: string
  description: string
  module: string
  status: TaskStatus
  acceptanceCriteria: string[]
  branch: string | null
  worktreePath: string | null
  bugReportPath: string | null
  createdAt: string
  updatedAt: string
}

// 日志
export interface LogEntry {
  ts: string
  stream: LogStream
  line: string
}

// Bug 报告
export interface BugReport {
  filename: string
  relativePath: string
  taskId: string
  module: string
  feature: string
  description: string
  createdAt: string
}

// 同步结果
export interface SyncResult {
  added: number
  unchanged: number
  total: number
}

// Review 请求
export interface ReviewRequest {
  result: 'pass' | 'fail'
  failedCriteria: string[]
}
