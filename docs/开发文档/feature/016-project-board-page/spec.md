# 016: 项目看板页

## 需求来源

PRD § 3.2 F-03、§ 3.3 F-05/F-06、§ 3.4 F-07、§ 6.2 任务看板；任务清单 M3-T03。

## 功能描述

在 `/project/:id` 页面以看板形式按任务状态分列展示该项目下的所有任务，并提供快捷操作。

## 验收标准

- [ ] 进入页面后自动获取并按状态分列展示任务
- [ ] 六列看板：待开发 / 开发中 / 待 review / 已完成 / 失败 / 已取消
- [ ] 每张任务卡片显示：类型标签（feature/bug）、标题、模块、更新时间
- [ ] `pending` 任务可触发执行；`in_progress` / `pending_review` / `pending` 任务可取消
- [ ] `failed` 任务可重置为 pending
- [ ] `pending_review` 任务可提交 review（pass / fail，fail 需选择未通过验收标准）
- [ ] 点击任务卡片跳转 `/project/:id/task/:taskId`
- [ ] 顶部显示项目名称及返回项目列表的导航

## 接口约定

- `GET  /api/projects/:projectId/tasks`              → `Task[]`
- `POST /api/tasks/:taskId/execute`                  → 触发执行
- `POST /api/tasks/:taskId/cancel`                   → 取消
- `POST /api/tasks/:taskId/reset`                    → 重置为 pending
- `POST /api/tasks/:taskId/review` + `{result, failedCriteria}` → 提交 review
