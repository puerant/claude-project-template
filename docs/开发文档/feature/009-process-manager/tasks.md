# 原子任务：进程管理器

> 任务编号：M2-T06

---

## T-01 创建进程管理服务

创建 `backend/app/services/process_manager.py`，定义 `ProcessManager` 类。

```python
import subprocess
from typing import Dict
from app.core.exceptions import GitError
from app.services.git_service import GitService


class ProcessManager:
    """进程管理器"""

    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.git_service = GitService()

    def start(self, task_id: str, worktree_path: str, prompt: str) -> None:
        """启动任务执行进程"""
        if task_id in self.processes:
            raise ValueError(f"任务 {task_id} 已在运行中")

        # 启动 claude --print <prompt>
        process = subprocess.Popen(
            ["claude", "--print", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=worktree_path,
            text=True,
        )

        self.processes[task_id] = process
        return None

    def stop(self, task_id: str) -> None:
        """停止任务执行进程"""
        if task_id not in self.processes:
            raise ValueError(f"任务 {task_id} 未在运行中")

        process = self.processes[task_id]
        process.terminate()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

        del self.processes[task_id]

    def get_process(self, task_id: str) -> subprocess.Popen | None:
        """获取任务进程对象"""
        return self.processes.get(task_id)
```

**操作文件**：`backend/app/services/process_manager.py`（新建）

---

## T-02 更新异常类

在 `backend/app/core/exceptions.py` 中添加进程相关异常。

```python
class ProcessError(HTTPException):
    """进程操作错误 (50003)"""

    def __init__(self, detail: str = "进程操作失败"):
        super().__init__(
            status_code=500, detail={"code": 50003, "message": detail}
        )
```

**操作文件**：`backend/app/core/exceptions.py`（修改）

---

## T-03 更新进程管理服务使用异常

修改 `ProcessManager` 的方法，使用自定义异常。

```python
from app.core.exceptions import ProcessError, GitError

class ProcessManager:
    # ... 现有代码 ...

    def start(self, task_id: str, worktree_path: str, prompt: str) -> None:
        """启动任务执行进程"""
        try:
            process = subprocess.Popen(...)
            self.processes[task_id] = process
            return None
        except Exception as e:
            raise ProcessError(f"启动进程异常: {str(e)}")

    def stop(self, task_id: str) -> None:
        """停止任务执行进程"""
        try:
            ...
        except Exception as e:
            raise ProcessError(f"停止进程异常: {str(e)}")
```

**操作文件**：`backend/app/services/process_manager.py`（修改）

---

## T-04 创建进程管理 API 路由

创建 `backend/app/routers/process.py`，实现进程管理的 API 端点。

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.process_manager import ProcessManager

router = APIRouter(prefix="/api/tasks", tags=["进程"])

process_manager = ProcessManager()


class StartProcessRequest(BaseModel):
    """启动进程请求"""
    prompt: str
    task_id: str


class StopProcessRequest(BaseModel):
    """停止进程请求"""
    task_id: str


@router.post("/{task_id}/start", response_model=dict)
async def start_process(req: StartProcessRequest):
    """启动任务执行进程"""
    return process_manager.start(req.task_id, ".worktrees/" + req.task_id, req.prompt)


@router.post("/{task_id}/stop", response_model=dict)
async def stop_process(req: StopProcessRequest):
    """停止任务执行进程"""
    process_manager.stop(req.task_id)
    return {"message": "任务已停止"}
```

**操作文件**：`backend/app/routers/process.py`（新建）

---

## T-05 注册进程路由

在 `backend/app/main.py` 中注册进程路由。

```python
from app.routers import project, task, process
```

**操作文件**：`backend/app/main.py`（修改）

---

## T-06 验证 API

验证进程管理功能是否正常工作。

```bash
cd backend
python -c "
from app.services.process_manager import ProcessManager
from app.models import Task, TaskType

manager = ProcessManager()

# 测试启动进程（模拟）
print('测试进程管理器...')
manager.start('test-task', '/tmp/test', '模拟的 Prompt')
print('进程已启动')

# 测试停止
manager.stop('test-task')
print('进程已停止')
"
```

**操作文件**：无（验证步骤）
