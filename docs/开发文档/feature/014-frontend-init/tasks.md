# 原子任务：前端项目初始化

> 任务编号：M3-T01

---

## T-01 脚手架 Vite + Vue3 + TypeScript 项目

在 worktree 根目录执行，在 `frontend/portal/` 下生成项目骨架。

```bash
npm create vite@latest frontend/portal -- --template vue-ts
```

**操作文件**：`frontend/portal/`（新建目录 + 多个脚手架文件）

---

## T-02 安装依赖

```bash
cd frontend/portal
npm install
npm install vue-router@4 axios
npm install -D tailwindcss@3 postcss autoprefixer
npx tailwindcss init -p
```

**操作文件**：`frontend/portal/package.json`、`node_modules/`（依赖安装）

---

## T-03 配置 TailwindCSS

更新 `frontend/portal/tailwind.config.js`，配置内容扫描路径；更新 `frontend/portal/src/style.css`，注入 Tailwind 指令。

tailwind.config.js:
```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: { extend: {} },
  plugins: [],
}
```

src/style.css:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**操作文件**：`frontend/portal/tailwind.config.js`、`frontend/portal/src/style.css`（修改）

---

## T-04 配置 Vite 代理

更新 `frontend/portal/vite.config.ts`，添加 `/api` → `http://localhost:8765` 代理。

```ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8765',
        changeOrigin: true,
      },
    },
  },
})
```

**操作文件**：`frontend/portal/vite.config.ts`（修改）

---

## T-05 创建类型定义

创建 `frontend/portal/src/types/index.ts`，定义所有业务实体的 TypeScript 类型。

```ts
// 通用响应包装
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

// 项目
export type TaskStatus = 'pending' | 'in_progress' | 'pending_review' | 'completed' | 'failed' | 'cancelled'
export type TaskType = 'feature' | 'bug'
export type LogStream = 'stdout' | 'stderr'

export interface TaskStats {
  total: number
  pending: number
  in_progress: number
  pending_review: number
  completed: number
  failed: number
  cancelled: number
}

export interface Project {
  id: string
  name: string
  path: string
  createdAt: string
  taskStats: TaskStats
}

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

export interface LogEntry {
  ts: string
  stream: LogStream
  line: string
}

export interface BugReport {
  filename: string
  relativePath: string
  taskId: string
  module: string
  feature: string
  description: string
  createdAt: string
}
```

**操作文件**：`frontend/portal/src/types/index.ts`（新建）

---

## T-06 创建 API 客户端

创建 `frontend/portal/src/api/client.ts`，导出 axios 实例。

```ts
import axios from 'axios'

export const client = axios.create({
  baseURL: '/api',
  timeout: 10000,
})
```

**操作文件**：`frontend/portal/src/api/client.ts`（新建）

---

## T-07 创建 API 封装函数

分别创建 `src/api/projects.ts`、`src/api/tasks.ts`、`src/api/logs.ts`、`src/api/bugs.ts`。

projects.ts:
```ts
import { client } from './client'
import type { Project } from '../types'

export const getProjects = () => client.get<Project[]>('/projects').then(r => r.data)
export const createProject = (name: string, path: string) =>
  client.post<Project>('/projects', { name, path }).then(r => r.data)
export const deleteProject = (id: string) => client.delete(`/projects/${id}`)
export const syncProject = (id: string) => client.post(`/projects/${id}/sync`).then(r => r.data)
```

tasks.ts:
```ts
import { client } from './client'
import type { Task } from '../types'

export const getTasks = (projectId: string, status?: string) =>
  client.get<Task[]>(`/projects/${projectId}/tasks`, { params: { status } }).then(r => r.data)
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
```

logs.ts:
```ts
import { client } from './client'
import type { LogEntry } from '../types'

export const getLogs = (taskId: string) =>
  client.get<LogEntry[]>(`/tasks/${taskId}/logs`).then(r => r.data)
export const getLogStreamUrl = (taskId: string) =>
  `/api/tasks/${taskId}/logs/stream`
```

bugs.ts:
```ts
import { client } from './client'
import type { BugReport } from '../types'

export const getBugReports = (projectId: string) =>
  client.get<BugReport[]>(`/projects/${projectId}/bugs`).then(r => r.data)
```

**操作文件**：`src/api/projects.ts`、`src/api/tasks.ts`、`src/api/logs.ts`、`src/api/bugs.ts`（新建）

---

## T-08 配置 Vue Router

创建 `frontend/portal/src/router/index.ts`，注册 5 个路由。

```ts
import { createRouter, createWebHistory } from 'vue-router'
import ProjectList from '../views/ProjectList.vue'
import ProjectBoard from '../views/ProjectBoard.vue'
import TaskDetail from '../views/TaskDetail.vue'
import LogView from '../views/LogView.vue'
import BugList from '../views/BugList.vue'

const routes = [
  { path: '/', component: ProjectList },
  { path: '/project/:id', component: ProjectBoard },
  { path: '/project/:id/task/:taskId', component: TaskDetail },
  { path: '/project/:id/task/:taskId/log', component: LogView },
  { path: '/project/:id/bugs', component: BugList },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
```

**操作文件**：`frontend/portal/src/router/index.ts`（新建）

---

## T-09 创建占位视图

创建 5 个占位 `<view>.vue` 文件（后续功能特性中实现）。

每个视图包含页面标题和简单说明，例如：

```vue
<script setup lang="ts">
</script>

<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold">项目列表</h1>
    <p class="text-gray-500 mt-2">（功能开发中）</p>
  </div>
</template>
```

**操作文件**：`src/views/ProjectList.vue`、`ProjectBoard.vue`、`TaskDetail.vue`、`LogView.vue`、`BugList.vue`（新建）

---

## T-10 更新 App.vue 和 main.ts

更新 `src/App.vue` 添加顶部导航 + `<RouterView>`；更新 `src/main.ts` 注册 router。

main.ts:
```ts
import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

createApp(App).use(router).mount('#app')
```

App.vue:
```vue
<script setup lang="ts">
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white border-b px-6 py-3 flex items-center gap-4">
      <RouterLink to="/" class="font-semibold text-gray-800 hover:text-blue-600">
        Claude Code Manager
      </RouterLink>
    </nav>
    <main class="container mx-auto px-6 py-8">
      <RouterView />
    </main>
  </div>
</template>
```

**操作文件**：`frontend/portal/src/main.ts`、`frontend/portal/src/App.vue`（修改）

---

## T-11 验证构建

```bash
cd frontend/portal
npm run build
```

验证：无 TypeScript 错误，无构建失败。

**操作文件**：无（验证步骤）
