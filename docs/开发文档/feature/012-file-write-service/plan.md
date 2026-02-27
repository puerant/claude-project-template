# 技术方案：文件写入模块

> 任务编号：M2-T09
> 模块：后端服务

---

## 架构设计

### 新增文件

| 文件 | 说明 |
| ---- | ---- |
| `backend/app/services/file_write_service.py` | FileWriteService：向被管理项目写入文档 |
| `backend/app/routers/review.py` | Review API 路由 |

### 修改文件

| 文件 | 修改内容 |
| ---- | -------- |
| `backend/app/services/project_service.py` | 添加 `get_project(project_id)` 方法 |
| `backend/app/main.py` | 注册 review 路由 |

---

## FileWriteService 设计

```python
class FileWriteService:
    def append_experience(project_path, task_title, failure_reason) -> None
    def create_bug_report(project_path, task, failed_criteria) -> str  # 返回相对路径
    def read_experience(project_path) -> str
```

- 写入目标是**被管理项目**，不是 Manager 自身的 data/ 目录
- `append_experience` 追加到 `<project_path>/docs/开发文档/经验总结.md`
- `create_bug_report` 写到 `<project_path>/docs/bug/<filename>.md`，返回相对路径

---

## Review 接口设计

```
POST /api/tasks/{taskId}/review
Body: { "result": "pass" | "fail", "failedCriteria": string[] }
```

### pass 路径

1. 校验任务状态为 `pending_review`
2. 调用 `git_service.commit_and_push(worktreePath, message)`
3. 调用 `git_service.remove_worktree(projectPath, worktreePath)`
4. 更新任务状态为 `completed`，清空 worktreePath
5. 保存任务，返回 `{ status, branch }`

### fail 路径

1. 校验任务状态为 `pending_review`
2. 校验 `failedCriteria` 非空
3. 调用 `file_write_service.create_bug_report(projectPath, task, failedCriteria)` 生成报告
4. 创建新的 `bug` 类型任务，关联 `bugReportPath`
5. 更新原任务状态为 `failed`，设置 `bugReportPath`
6. 保存任务列表（原任务 + 新 bug 任务）
7. 返回 `{ status, bugReportPath, newBugTaskId }`

---

## 依赖关系

```
review.py
  └─ TaskService.get_task_by_id()
  └─ TaskService.save_tasks()
  └─ ProjectService.get_project()
  └─ FileWriteService.create_bug_report()
  └─ GitService.commit_and_push()
  └─ GitService.remove_worktree()
```
