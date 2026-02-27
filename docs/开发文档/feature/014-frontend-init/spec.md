# 功能需求：前端项目初始化

> 任务编号：M3-T01
> 模块：前端

---

## 用户故事

作为开发者，我需要一个可运行的前端项目骨架，包含路由、类型定义、API 封装层，以便后续各页面功能可以在此基础上独立开发。

---

## 功能描述

### 3.1 项目骨架

在 `frontend/portal/` 目录下创建基于 **Vite + Vue3 + TypeScript** 的前端项目，包含：

- TailwindCSS 样式框架
- Vue Router 4（History 模式）
- axios HTTP 客户端

### 3.2 代理配置

开发时将 `/api` 请求代理到后端 `http://localhost:8765`，避免跨域。

### 3.3 TypeScript 类型定义

在 `src/types/index.ts` 中定义所有业务实体类型，与后端接口契约一致：

- `Project`、`TaskStats`
- `Task`、`TaskType`、`TaskStatus`
- `LogEntry`、`LogStream`
- `BugReport`
- `ApiResponse<T>`

### 3.4 API 封装层

按域分文件封装所有后端接口：

| 文件 | 覆盖接口 |
| ---- | -------- |
| `src/api/projects.ts` | 项目增删、同步 |
| `src/api/tasks.ts` | 任务查询、执行、review |
| `src/api/logs.ts` | 日志历史、SSE 流 |
| `src/api/bugs.ts` | Bug 报告列表 |

### 3.5 路由配置

| 路由 | 对应视图 |
| ---- | -------- |
| `/` | `ProjectList.vue` |
| `/project/:id` | `ProjectBoard.vue` |
| `/project/:id/task/:taskId` | `TaskDetail.vue` |
| `/project/:id/task/:taskId/log` | `LogView.vue` |
| `/project/:id/bugs` | `BugList.vue` |

---

## 验收标准

- [ ] `frontend/portal/` 目录存在，`npm run build` 通过（无报错）
- [ ] TailwindCSS 正常工作
- [ ] 所有路由可访问（返回对应占位视图）
- [ ] API 封装层中所有函数有正确的类型签名
- [ ] 类型定义覆盖所有后端实体

---

## 边界情况

| 场景 | 预期行为 |
| ---- | -------- |
| 后端未启动时访问 | API 调用返回 Promise rejected，页面显示错误状态 |
| 访问不存在的路由 | 重定向到 `/` |
