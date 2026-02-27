# 功能需求：文件写入模块

> 任务编号：M2-T09
> 模块：后端服务

---

## 用户故事

作为 Claude Code Manager，当任务执行失败或 Review 不通过时，我需要自动向被管理项目写入结构化文档（经验总结、Bug 报告），同时提供读取经验总结的能力，以便在后续任务执行时注入已有经验。

---

## 功能描述

### 3.1 向经验总结追加失败经验（F-13）

当任务 Review 失败时，向被管理项目的 `docs/开发文档/经验总结.md` 末尾追加以下格式内容：

```markdown
---

## YYYY-MM-DD 任务标题

**问题**：<失败原因>

**原因**：（待分析）

**解决方案**：（待填写）
```

### 3.2 生成 Bug 报告文件（F-12）

当任务 Review 不通过时，在被管理项目的 `docs/bug/` 目录下生成 Bug 报告 `.md` 文件。

文件命名规则：`<YYYY-MM-DD>-<模块>-<功能>-<简短描述>.md`

### 3.3 读取经验总结全文（F-14）

提供读取被管理项目 `docs/开发文档/经验总结.md` 全文的能力（已在 PromptService 中使用）。

### 3.4 Review 接口（POST /api/tasks/{taskId}/review）

用户在任务详情页提交 Review 结果，系统据此执行：

- **pass**：git commit + push → 清理 worktree → 任务状态 `completed`
- **fail**：生成 Bug 报告 → 创建新 bug 任务 → 追加经验总结 → 任务状态 `failed`

---

## 验收标准

- [ ] `FileWriteService.append_experience` 能向被管理项目追加格式化的经验总结
- [ ] `FileWriteService.create_bug_report` 能在被管理项目 `docs/bug/` 下生成 Bug 报告 `.md`
- [ ] `FileWriteService.read_experience` 能读取被管理项目经验总结全文
- [ ] `POST /api/tasks/{taskId}/review` 接口实现 pass/fail 两条路径
- [ ] Review pass：任务状态变为 `completed`，worktree 被清理
- [ ] Review fail：生成 Bug 报告、创建 bug 任务、任务状态变为 `failed`
- [ ] `ProjectService.get_project(project_id)` 方法可用（review 接口依赖）

---

## 边界情况

| 场景 | 预期行为 |
| ---- | -------- |
| `经验总结.md` 不存在（读） | 返回空字符串 |
| `经验总结.md` 父目录不存在（写） | 自动创建 |
| `docs/bug/` 目录不存在 | 自动创建 |
| Review 时任务状态不为 `pending_review` | 返回 409 错误 |
| Review fail 但 failedCriteria 为空 | 返回 400 错误 |
| git commit/push 失败（pass 路径） | 捕获异常、记录日志，状态仍置为 completed |
