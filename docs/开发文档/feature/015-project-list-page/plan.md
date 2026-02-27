# 015: 项目列表页 — 实现方案

## 技术方案

- 使用 `composables/useProjects.ts` 封装所有状态与 API 调用，视图只负责渲染
- `ProjectList.vue` 通过 composable 获取列表、执行操作
- 新增项目通过内联弹窗（`v-if` 控制）完成，无需路由跳转
- 同步结果以 Toast / 行内提示展示，不阻断操作流

## 文件清单

| 路径 | 操作 |
|------|------|
| `frontend/portal/src/composables/useProjects.ts` | 新建 |
| `frontend/portal/src/views/ProjectList.vue` | 修改（替换占位内容） |

## 依赖关系

- `frontend/portal/src/api/projects.ts` — 已存在，提供全部所需方法
- `frontend/portal/src/types/index.ts` — 已存在，`Project`、`SyncResult` 类型已定义
