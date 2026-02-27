# 015: 项目列表页

## 需求来源

PRD § 3.1 F-01 添加项目、F-02 项目列表；任务清单 M3-T02。

## 功能描述

在前端门户首页（`/`）展示所有已添加项目的概览卡片，并支持新增、删除、同步项目操作。

## 验收标准

- [ ] 页面加载后自动获取并展示项目列表
- [ ] 每个项目卡片显示：名称、路径、任务统计（总数及各状态数量）
- [ ] 支持新增项目（弹窗输入名称和路径）
- [ ] 支持删除项目（二次确认）
- [ ] 支持同步项目（重新解析任务清单，显示同步结果）
- [ ] 点击项目卡片跳转到 `/project/:id`

## 接口约定

- `GET  /api/projects`          → `Project[]`
- `POST /api/projects`          → `Project`（body: `{ name, path }`）
- `DELETE /api/projects/:id`    → 204
- `POST /api/projects/:id/sync` → `SyncResult`（`{ added, unchanged, total }`）
