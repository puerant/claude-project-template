# 原子任务：输出解析器与执行引擎整合

> 任务编号：M2-T07

---

## T-01 创建输出解析器

创建 `backend/app/services/output_parser.py`，定义 `OutputParser` 类。

```python
import re
from typing import Optional


class OutputParser:
    """Claude Code 输出解析器"""

    PATTERN_SUCCESS = r"^SUCCESS$"
    PATTERN_FAILURE = r"^FAILURE:\s*(.+)$"

    def parse(self, output: str) -> tuple[bool, Optional[str]]:
        """
        解析输出，识别成功或失败标记

        Returns:
            (is_success, failure_reason): is_success=True 表示成功，False 表示失败；
            failure_reason 仅在失败时包含原因字符串
        """
        lines = output.strip().split("\n")

        # 从最后一行开始匹配
        for line in reversed(lines):
            line = line.strip()

            # 匹配 SUCCESS
            if re.match(self.PATTERN_SUCCESS, line, re.IGNORECASE):
                return (True, None)

            # 匹配 FAILURE: <原因>
            match = re.match(self.PATTERN_FAILURE, line, re.IGNORECASE)
            if match:
                return (False, match.group(1).strip())

        # 未找到结果标记
        return (None, None)

    def has_result(self, output: str) -> bool:
        """检查输出中是否包含结果标记"""
        result, _ = self.parse(output)
        return result is not None
```

**操作文件**：`backend/app/services/output_parser.py`（新建）

---

## T-02 创建执行引擎服务

创建 `backend/app/services/execution_service.py`，定义 `ExecutionService` 类。

```python
from pathlib import Path
from app.models import Task, TaskStatus
from app.services.git_service import GitService
from app.services.process_manager import ProcessManager
from app.services.prompt_service import PromptService
from app.services.output_parser import OutputParser
from app.core.file_utils import read_json, write_json
from app.core.exceptions import InvalidStatusTransitionError


class ExecutionService:
    """任务执行引擎"""

    def __init__(self):
        self.git_service = GitService()
        self.process_manager = ProcessManager()
        self.prompt_service = PromptService()
        self.output_parser = OutputParser()
        self.data_dir = Path(__file__).parent.parent.parent / "data"

    def execute(self, task: Task, project_path: str) -> Task:
        """
        执行任务流程：
        1. 校验状态（必须是 pending）
        2. 创建分支
        3. 创建 worktree
        4. 构建 Prompt
        5. 启动进程
        6. 更新状态为 in_progress
        """
        # 校验状态
        if task.status != TaskStatus.PENDING:
            raise InvalidStatusTransitionError()

        # 生成分支名和 worktree 路径
        task_id = task.id
        branch = f"feat/{task_id}"
        worktree_path = str(self.data_dir / "worktrees" / task_id)

        # 创建分支
        self.git_service.create_branch(project_path, branch)

        # 创建 worktree
        self.git_service.create_worktree(project_path, worktree_path, branch)

        # 构建 Prompt
        prompt = self.prompt_service.build_prompt(task, project_path)

        # 启动进程
        self.process_manager.start(task_id, worktree_path, prompt)

        # 更新任务状态
        task.status = TaskStatus.IN_PROGRESS
        task.branch = branch
        task.worktreePath = worktree_path

        return task

    def cancel(self, task: Task) -> Task:
        """
        取消任务：
        1. 终止进程
        2. 删除 worktree
        3. 更新状态为 cancelled
        """
        if task.worktreePath:
            # 终止进程
            try:
                self.process_manager.stop(task.id)
            except Exception:
                pass

            # 删除 worktree
            try:
                self.git_service.remove_worktree(".", task.worktreePath)
            except Exception:
                pass

        # 更新状态
        task.status = TaskStatus.CANCELLED
        task.branch = None
        task.worktreePath = None

        return task

    def reset(self, task: Task) -> Task:
        """
        重置失败任务：
        1. 删除 worktree
        2. 清空 branch 和 worktreePath
        3. 更新状态为 pending
        """
        if task.worktreePath:
            # 删除 worktree
            try:
                self.git_service.remove_worktree(".", task.worktreePath)
            except Exception:
                pass

        # 更新状态
        task.status = TaskStatus.PENDING
        task.branch = None
        task.worktreePath = None

        return task
```

**操作文件**：`backend/app/services/execution_service.py`（新建）

---

## T-03 更新任务服务集成执行引擎

在 `backend/app/services/task_service.py` 中添加执行相关方法。

```python
from app.services.execution_service import ExecutionService

class TaskService:
    def __init__(self):
        self.project_service = ProjectService()
        self.execution_service = ExecutionService()
        # ... 现有代码 ...

    def execute_task(self, project_id: str, task_id: str) -> Task:
        """执行任务"""
        # 获取任务
        task = self.get_task(project_id, task_id)

        # 获取项目路径
        project = self.project_service.get_project(project_id)
        project_path = project.path

        # 执行任务
        updated_task = self.execution_service.execute(task, project_path)

        # 保存任务
        self._save_task(updated_task)

        return updated_task

    def cancel_task(self, task_id: str) -> Task:
        """取消任务"""
        task = self.get_task_by_id(task_id)

        # 取消任务
        updated_task = self.execution_service.cancel(task)

        # 保存任务
        self._save_task(updated_task)

        return updated_task

    def reset_task(self, task_id: str) -> Task:
        """重置任务"""
        task = self.get_task_by_id(task_id)

        # 重置任务
        updated_task = self.execution_service.reset(task)

        # 保存任务
        self._save_task(updated_task)

        return updated_task
```

**操作文件**：`backend/app/services/task_service.py`（修改）

---

## T-04 创建执行 API 路由

创建 `backend/app/routers/execution.py`，实现任务执行的 API 端点。

```python
from fastapi import APIRouter
from app.services.task_service import TaskService

router = APIRouter(prefix="/api/tasks", tags=["执行"])

task_service = TaskService()


@router.post("/{taskId}/execute")
async def execute_task(taskId: str):
    """执行任务"""
    return task_service.execute_task(None, taskId)


@router.post("/{taskId}/cancel")
async def cancel_task(taskId: str):
    """取消任务"""
    return task_service.cancel_task(taskId)
```

**操作文件**：`backend/app/routers/execution.py`（新建）

---

## T-05 注册执行路由

在 `backend/app/main.py` 中注册执行路由。

```python
from app.routers import project, task, process, execution
```

**操作文件**：`backend/app/main.py`（修改）

---

## T-06 验证执行引擎

验证执行引擎功能是否正常工作。

```bash
cd backend
python -c "
from app.services.output_parser import OutputParser

parser = OutputParser()

# 测试成功输出
output1 = '任务完成\\nSUCCESS'
result1, reason1 = parser.parse(output1)
print(f'成功测试: {result1}, 原因: {reason1}')

# 测试失败输出
output2 = '任务失败\\nFAILURE: 依赖库未安装'
result2, reason2 = parser.parse(output2)
print(f'失败测试: {result2}, 原因: {reason2}')

# 测试无结果标记
output3 = '执行中...'
result3, reason3 = parser.parse(output3)
print(f'无标记测试: {result3}, 原因: {reason3}')
"
```

**操作文件**：无（验证步骤）
