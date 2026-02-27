# 018: 日志页 — 实现方案

## 技术方案

- `useLogView.ts`：封装历史日志加载 + SSE 订阅逻辑；`onUnmounted` 时关闭 EventSource 防止泄漏；
  用 `autoScroll` ref 控制是否自动滚动到底部
- `LogView.vue`：消费 composable，日志区域用等宽字体 `<div>` 渲染，监听 scroll 事件切换 autoScroll；
  同时加载任务信息（`getTask`）用于面包屑和判断是否需要 SSE

## 文件清单

| 路径 | 操作 |
|------|------|
| `frontend/portal/src/composables/useLogView.ts` | 新建 |
| `frontend/portal/src/views/LogView.vue` | 修改（替换占位内容） |

## 依赖关系

- `frontend/portal/src/api/logs.ts` — 已存在，提供 `getLogs` / `getLogStreamUrl`
- `frontend/portal/src/api/tasks.ts` — 已存在，提供 `getTask`
- `frontend/portal/src/types/index.ts` — 已存在，`LogEntry`、`Task` 已定义
