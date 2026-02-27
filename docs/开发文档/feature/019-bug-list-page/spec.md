# 019: Bug 列表页

## 需求来源

PRD § 6.1 页面列表；任务清单 M3-T06。

## 功能描述

在 `/project/:id/bugs` 页面展示项目下所有 Bug 报告，支持跳转到关联任务详情。

## 验收标准

- [ ] 页面加载后自动获取 Bug 报告列表并展示
- [ ] 每条 Bug 显示：文件名、模块、功能、描述、创建时间
- [ ] 点击 Bug 条目可跳转到关联任务详情（`/project/:id/task/:taskId`）
- [ ] 无 Bug 时显示空状态
- [ ] 面包屑导航：项目列表 → 看板 → Bug 列表

## 接口约定

- `GET /api/projects/:projectId/bugs` → `BugReport[]`
