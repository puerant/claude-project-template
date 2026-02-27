# 017: 任务详情页 — 实现方案

## 技术方案

- `useTaskDetail.ts`：封装单任务获取与所有状态操作（execute / cancel / reset / review），
  暴露 `task`、`loading`、`error`、`operating` 给视图使用
- `TaskDetail.vue`：消费 composable，layout 分左右两栏（基本信息 + 描述）；
  Markdown 渲染用 `<pre>` 保持简洁，无需引入额外依赖；review 弹窗复用看板页同款设计

## 文件清单

| 路径 | 操作 |
|------|------|
| `frontend/portal/src/composables/useTaskDetail.ts` | 新建 |
| `frontend/portal/src/views/TaskDetail.vue` | 修改（替换占位内容） |

## 依赖关系

- `frontend/portal/src/api/tasks.ts` — 已存在
- `frontend/portal/src/types/index.ts` — 已存在，`Task`、`TaskStatus` 已定义
