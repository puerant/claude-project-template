# 原子任务：文件写入模块

> 任务编号：M2-T09

---

## T-01 创建文件写入服务

创建 `backend/app/services/file_write_service.py`，定义 `FileWriteService` 类。

```python
from pathlib import Path
from datetime import datetime
from app.models import Task


class FileWriteService:
    """文件写入服务：向被管理项目写入文档"""

    def append_experience(self, project_path: str, task_title: str, failure_reason: str) -> None:
        """向被管理项目的经验总结.md 追加失败经验"""
        exp_file = Path(project_path) / "docs/开发文档/经验总结.md"
        exp_file.parent.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        content = f"""
---

## {date_str} {task_title}

**问题**：{failure_reason}

**原因**：（待分析）

**解决方案**：（待填写）
"""
        with open(exp_file, "a", encoding="utf-8") as f:
            f.write(content)

    def create_bug_report(self, project_path: str, task: Task, failed_criteria: list[str]) -> str:
        """
        在被管理项目的 docs/bug/ 目录生成 Bug 报告文件
        Returns:
            relative_path: Bug 报告相对于项目根目录的路径
        """
        bug_dir = Path(project_path) / "docs/bug"
        bug_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%Y-%m-%d %H:%M")

        short_desc = failed_criteria[0][:20] if failed_criteria else "测试失败"
        raw_name = f"{date_str}-{task.module}-{task.title[:10]}-{short_desc}.md"
        for ch in r'/\:*?"<>|':
            raw_name = raw_name.replace(ch, "-")
        filename = raw_name

        bug_file = bug_dir / filename

        acceptance_text = "\n".join(f"- {c}" for c in task.acceptanceCriteria)
        failed_text = "\n".join(f"- {c}" for c in failed_criteria)

        content = f"""# Bug 报告

- **时间**：{time_str}
- **模块**：{task.module}
- **功能**：{task.title}
- **任务 ID**：{task.id}
- **分支**：{task.branch or "未知"}

## 问题描述

{failed_text}

## 复现步骤

（待填写）

## 期望结果

{acceptance_text}

## 实际结果

（测试失败的实际现象）

## 状态

- [ ] 待修复
"""
        with open(bug_file, "w", encoding="utf-8") as f:
            f.write(content)

        return f"docs/bug/{filename}"

    def read_experience(self, project_path: str) -> str:
        """读取被管理项目经验总结.md 全文"""
        exp_file = Path(project_path) / "docs/开发文档/经验总结.md"
        if not exp_file.exists():
            return ""
        with open(exp_file, "r", encoding="utf-8") as f:
            return f.read()
```

**操作文件**：`backend/app/services/file_write_service.py`（新建）

---

## T-02 为 ProjectService 添加 get_project 方法

在 `backend/app/services/project_service.py` 的 `add_project` 方法之后添加 `get_project` 方法。

```python
def get_project(self, project_id: str) -> Project:
    """根据 ID 获取项目"""
    projects = self.list_projects()
    for p in projects:
        if p.id == project_id:
            return p
    raise ProjectNotFoundError()
```

**操作文件**：`backend/app/services/project_service.py`（修改）

---

## T-03 创建 review 路由

创建 `backend/app/routers/review.py`，实现 `POST /api/tasks/{taskId}/review` 端点。

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.services.task_service import TaskService
from app.services.file_write_service import FileWriteService
from app.services.project_service import ProjectService
from app.services.git_service import GitService
from app.models import TaskStatus, TaskType, Task
from app.core.exceptions import InvalidStatusTransitionError

router = APIRouter(prefix="/api/tasks", tags=["review"])

task_service = TaskService()
file_write_service = FileWriteService()
project_service = ProjectService()
git_service = GitService()


class ReviewRequest(BaseModel):
    result: str
    failedCriteria: List[str] = []


@router.post("/{taskId}/review")
async def review_task(taskId: str, body: ReviewRequest):
    """提交 Review 结果"""
    task, project_id = task_service.get_task_by_id(taskId)

    if task.status != TaskStatus.PENDING_REVIEW:
        raise InvalidStatusTransitionError()

    project = project_service.get_project(project_id)
    project_path = project.path

    tasks = task_service.list_tasks(project_id)

    if body.result == "pass":
        if task.worktreePath and task.branch:
            try:
                git_service.commit_and_push(task.worktreePath, f"feat: {task.title}")
            except Exception:
                pass
            try:
                git_service.remove_worktree(project_path, task.worktreePath)
            except Exception:
                pass

        task.status = TaskStatus.COMPLETED
        task.worktreePath = None
        task.updatedAt = datetime.now().isoformat()

        for i, t in enumerate(tasks):
            if t.id == taskId:
                tasks[i] = task
                break
        task_service.save_tasks(project_id, tasks)

        return {"status": "completed", "branch": task.branch}

    elif body.result == "fail":
        if not body.failedCriteria:
            raise HTTPException(
                status_code=400,
                detail={"code": 40001, "message": "failedCriteria 不能为空"}
            )

        bug_report_path = file_write_service.create_bug_report(
            project_path, task, body.failedCriteria
        )

        new_bug_task = Task(
            projectId=project_id,
            type=TaskType.BUG,
            title=f"修复: {task.title}",
            description=(
                f"关联 Bug 报告：{bug_report_path}\n\n"
                f"失败原因：\n" + "\n".join(f"- {c}" for c in body.failedCriteria)
            ),
            module=task.module,
            acceptanceCriteria=body.failedCriteria,
            bugReportPath=bug_report_path,
        )

        task.status = TaskStatus.FAILED
        task.bugReportPath = bug_report_path
        task.updatedAt = datetime.now().isoformat()

        for i, t in enumerate(tasks):
            if t.id == taskId:
                tasks[i] = task
                break
        tasks.append(new_bug_task)
        task_service.save_tasks(project_id, tasks)

        return {
            "status": "failed",
            "bugReportPath": bug_report_path,
            "newBugTaskId": new_bug_task.id,
        }

    else:
        raise HTTPException(
            status_code=400,
            detail={"code": 40001, "message": "result 必须为 pass 或 fail"}
        )
```

**操作文件**：`backend/app/routers/review.py`（新建）

---

## T-04 注册 review 路由

在 `backend/app/main.py` 中导入并注册 review 路由。

```python
from app.routers import project, task, process, execution, log, review

# 在 app.include_router(log.router) 之后添加：
app.include_router(review.router)
```

**操作文件**：`backend/app/main.py`（修改）

---

## T-05 验证文件写入服务

验证 FileWriteService 各方法是否正常工作。

```bash
cd backend
python -c "
import tempfile, os
from pathlib import Path

# 创建临时项目目录模拟被管理项目
with tempfile.TemporaryDirectory() as tmpdir:
    # 准备目录结构
    Path(tmpdir, 'docs', '开发文档').mkdir(parents=True)

    from app.services.file_write_service import FileWriteService
    from app.models import Task, TaskType

    svc = FileWriteService()

    # 测试 read_experience（文件不存在）
    content = svc.read_experience(tmpdir)
    assert content == '', f'expected empty, got {repr(content)}'
    print('read_experience (not exists): OK')

    # 测试 append_experience
    svc.append_experience(tmpdir, '用户登录功能', '依赖库未安装')
    content = svc.read_experience(tmpdir)
    assert '用户登录功能' in content and '依赖库未安装' in content
    print('append_experience: OK')

    # 测试 create_bug_report
    task = Task(
        projectId='proj-1',
        type=TaskType.FEATURE,
        title='登录功能',
        description='desc',
        module='用户模块',
        acceptanceCriteria=['密码正确时可登录'],
        branch='feat/test',
    )
    path = svc.create_bug_report(tmpdir, task, ['错误提示未显示'])
    assert path.startswith('docs/bug/')
    assert Path(tmpdir, path).exists()
    print(f'create_bug_report: OK -> {path}')

print('所有验证通过')
"
```

**操作文件**：无（验证步骤）
