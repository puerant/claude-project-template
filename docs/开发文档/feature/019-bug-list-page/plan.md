# 019: Bug 列表页 — 实现方案

## 技术方案

- `useBugList.ts`：封装 `getBugReports` 调用，暴露 `bugs / loading / error / fetchBugs`
- `BugList.vue`：消费 composable，列表展示 Bug 报告卡片；点击卡片跳转到任务详情；
  面包屑使用项目 ID 构建看板链接

## 文件清单

| 路径 | 操作 |
|------|------|
| `frontend/portal/src/composables/useBugList.ts` | 新建 |
| `frontend/portal/src/views/BugList.vue` | 修改（替换占位内容） |

## 依赖关系

- `frontend/portal/src/api/bugs.ts` — 已存在，提供 `getBugReports`
- `frontend/portal/src/types/index.ts` — 已存在，`BugReport` 已定义
