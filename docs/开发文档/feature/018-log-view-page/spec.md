# 018: 日志页

## 需求来源

PRD § 3.7 F-16 执行日志；任务清单 M3-T05。

## 功能描述

在 `/project/:id/task/:taskId/log` 页面展示任务执行日志，支持历史日志查看与实时 SSE 流。

## 验收标准

- [ ] 页面加载后自动获取历史日志并展示
- [ ] 任务处于 `in_progress` 状态时，自动通过 SSE 订阅实时日志，新行追加到底部
- [ ] SSE 收到 `done` / `error` 事件后断开连接
- [ ] 日志行显示：时间戳、流类型（stdout=白/stderr=橙）、内容
- [ ] 自动滚动到最新日志，可手动滚动后停止自动滚动
- [ ] 面包屑导航：项目列表 → 看板 → 任务详情 → 日志
- [ ] 无日志时显示空状态

## 接口约定

- `GET /api/tasks/:taskId/logs`         → `LogEntry[]`（历史）
- `GET /api/tasks/:taskId/logs/stream`  → SSE 实时流（event: log / done / error）
- `GET /api/tasks/:taskId`              → `Task`（用于判断状态和展示标题）
