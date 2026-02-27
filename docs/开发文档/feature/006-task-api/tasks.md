# 原子任务：任务管理模块与 API

> 任务编号：M2-T03

---

## T-01 扩展 TaskService 添加任务查询方法

在 `TaskService` 中添加任务查询和状态流转方法。

```python
from typing import List, Optional
from app.models import Task, TaskStatus

class TaskService:
    # ... 现有代码 ...

    def get_task(self, project_id: str, task_id: str) -> Task | None:
        """获取指定任务详情"""
        tasks = self.list_tasks(project_id)
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def cancel_task(self, project_id: str, task_id: str) -> Task:
        """取消任务"""
        tasks = self.list_tasks(project_id)
        for i, task in enumerate(tasks):
            if task.id == task_id:
                if task.status not in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.PENDING_REVIEW]:
                    raise ValueError("只能取消 pending / in_progress / pending_review 状态的任务")

                task.status = TaskStatus.CANCELLED
                tasks[i] = task
                break

        self.save_tasks(project_id, tasks)
        return task

    def reset_task(self, project_id: str, task_id: str) -> Task:
        """重置任务"""
        tasks = self.list_tasks(project_id)
        for i, task in enumerate(tasks):
            if task.id == task_id:
                if task.status != TaskStatus.FAILED:
                    raise ValueError("只能重置 failed 状态的任务")

                task.status = TaskStatus.PENDING
                task.branch = None
                task.worktreePath = None
                tasks[i] = task
                break

        self.save_tasks(project_id, tasks)
        return task
```

**操作文件**：`backend/app/services/task_service.py`（修改）

---

## T-02 扩展 TaskService 添加任务列表查询方法

在 `TaskService` 中添加支持过滤的任务列表查询方法。

```python
from typing import Optional
from app.models import TaskType

class TaskService:
    # ... 现有代码 ...

    def list_tasks_filtered(
        self,
        project_id: str,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None
    ) -> List[Task]:
        """获取项目的任务列表（支持过滤）"""
        all_tasks = self.list_tasks(project_id)

        filtered = all_tasks
        if status:
            filtered = [t for t in filtered if t.status == status]
        if task_type:
            filtered = [t for t in filtered if t.type == task_type]

        # 按 updatedAt 降序排列
        filtered.sort(key=lambda t: t.updatedAt, reverse=True)
        return filtered
```

**操作文件**：`backend/app/services/task_service.py`（修改）

---

## T-03 更新异常类

在 `backend/app/core/exceptions.py` 中添加任务相关异常。

```python
from app.models import TaskStatus

class InvalidStatusTransitionError(HTTPException):
    """非法状态流转错误 (40901)"""

    def __init__(self):
        super().__init__(
            status_code=409,
            detail={"code": 40901, "message": "非法状态流转"}
        )
```

**操作文件**：`backend/app/core/exceptions.py`（修改）

---

## T-04 扩展 TaskService 使用新异常

更新 `TaskService` 中的状态流转方法，使用新异常。

```python
from app.core.exceptions import InvalidStatusTransitionError

    def cancel_task(self, project_id: str, task_id: str) -> Task:
        """取消任务"""
        tasks = self.list_tasks(project_id)
        for i, task in enumerate(tasks):
            if task.id == task_id:
                if task.status not in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.PENDING_REVIEW]:
                    raise InvalidStatusTransitionError()

                task.status = TaskStatus.CANCELLED
                tasks[i] = task
                break

        self.save_tasks(project_id, tasks)
        return task

    def reset_task(self, project_id: str, task_id: str) -> Task:
        """重置任务"""
        tasks = self.list_tasks(project_id)
        for i, task in enumerate(tasks):
            if task.id == task_id:
                if task.status != TaskStatus.FAILED:
                    raise InvalidStatusTransitionError()

                task.status = TaskStatus.PENDING
                task.branch = None
                task.worktreePath = None
                tasks[i] = task
                break

        self.save_tasks(project_id, tasks)
        return task
```

**操作文件**：`backend/app/services/task_service.py`（修改）

---

## T-05 扩展任务路由

在 `backend/app/routers/task.py` 中添加任务管理的 API 端点。

```python
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.services.task_service import TaskService
from app.models import TaskType, TaskStatus

router = APIRouter(prefix="/api", tags=["任务"])

task_service = TaskService()


@router.get("/projects/{project_id}/tasks", response_model=list[Task])
async def list_project_tasks(
    project_id: str,
    status: Optional[TaskStatus] = Query(None),
    task_type: Optional[TaskType] = Query(None)
):
    """获取项目的任务列表"""
    return task_service.list_tasks_filtered(project_id, status, task_type)


@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """获取任务详情"""
    # 遍历所有项目查找任务
    from app.services.project_service import ProjectService
    project_service = ProjectService()
    projects = project_service.list_projects()

    for project in projects:
        task = task_service.get_task(project.id, task_id)
        if task:
            return task

    raise HTTPException(status_code=404, detail={"code": 40401, "message": "任务不存在"})


@router.post("/tasks/{task_id}/cancel", response_model=Task)
async def cancel_task(task_id: str):
    """取消任务"""
    from app.services.project_service import ProjectService
    project_service = ProjectService()
    projects = project_service.list_projects()

    for project in projects:
        task = task_service.get_task(project.id, task_id)
        if task:
            return task_service.cancel_task(project.id, task_id)

    raise HTTPException(status_code=404, detail={"code": 40401, "message": "任务不存在"})


@router.post("/tasks/{task_id}/reset", response_model=Task)
async def reset_task(task_id: str):
    """重置任务"""
    from app.services.project_service import ProjectService
    project_service = ProjectService()
    projects = project_service.list_projects()

    for project in projects:
        task = task_service.get_task(project.id, task_id)
        if task:
            return task_service.reset_task(project.id, task_id)

    raise HTTPException(status_code=404, detail={"code": 40401, "message": "任务不存在"})
```

**操作文件**：`backend/app/routers/task.py`（修改）

---

## T-06 验证 API

启动服务并测试 API。

```bash
cd backend
python main.py
```

另开终端测试：

```bash
# 获取任务列表（带过滤）
curl "http://localhost:8765/api/projects/{project-id}/tasks?status=pending"
curl "http://localhost:8765/api/projects/{project-id}/tasks?type=feature"

# 取消任务
curl -X POST http://localhost:8765/api/tasks/{task-id}/cancel

# 重置任务
curl -X POST http://localhost:8765/api/tasks/{task-id}/reset
```

**操作文件**：无（验证步骤）
