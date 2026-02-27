# 016: 项目看板页 — 实现方案

## 技术方案

- `useTaskBoard.ts`：封装任务列表获取与所有操作（execute / cancel / reset / review），
  暴露按状态分组的 `columns` 计算属性，供视图直接渲染
- `ProjectBoard.vue`：消费 composable，渲染六列看板；review 弹窗以 `v-if` 控制，
  包含验收标准多选 checkbox（fail 路径）

## 文件清单

| 路径 | 操作 |
|------|------|
| `frontend/portal/src/composables/useTaskBoard.ts` | 新建 |
| `frontend/portal/src/views/ProjectBoard.vue` | 修改（替换占位内容） |

## 依赖关系

- `frontend/portal/src/api/tasks.ts` — 已存在，提供全部所需方法
- `frontend/portal/src/types/index.ts` — 已存在，`Task`、`TaskStatus` 类型已定义
- `frontend/portal/src/api/projects.ts` — 用于获取项目名称（`getProjects`）
