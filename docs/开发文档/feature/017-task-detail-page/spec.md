# 017: 任务详情页

## 需求来源

PRD § 3.7 F-15 任务详情页；任务清单 M3-T04。

## 功能描述

在 `/project/:id/task/:taskId` 页面展示任务完整信息，并提供状态相关的操作入口。

## 验收标准

- [ ] 页面加载后自动获取并展示任务详情
- [ ] 显示基本信息：类型标签、标题、模块、状态徽章、创建时间、更新时间
- [ ] 显示任务描述（Markdown 原文渲染）
- [ ] 显示验收标准列表（可视化展示）
- [ ] 显示关联分支和 worktree 路径（若有）
- [ ] 根据当前状态显示操作按钮：执行 / 取消 / 重置 / review
- [ ] review 弹窗（pass / fail，fail 时选择未通过验收标准）
- [ ] 查看日志按钮，跳转 `/project/:id/task/:taskId/log`
- [ ] 面包屑导航：项目列表 → 项目看板 → 任务详情

## 接口约定

- `GET  /api/tasks/:taskId`                          → `Task`
- `POST /api/tasks/:taskId/execute`
- `POST /api/tasks/:taskId/cancel`
- `POST /api/tasks/:taskId/reset`
- `POST /api/tasks/:taskId/review` + `{result, failedCriteria}`
