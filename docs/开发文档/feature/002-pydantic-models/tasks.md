# 原子任务：Pydantic 数据模型定义

> 任务编号：M1-T02

---

## T-01 创建 models 目录和 __init__.py

创建 `backend/app/models/` 目录及其 `__init__.py` 文件。

```bash
mkdir -p backend/app/models
touch backend/app/models/__init__.py
```

**操作文件**：新建 1 个目录、1 个文件

---

## T-02 创建项目模型

创建 `backend/app/models/project.py` 文件，定义 `Project` 和 `TaskStats` 模型。

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TaskStats(BaseModel):
    """任务统计数据"""
    total: int = 0
    pending: int = 0
    in_progress: int = 0
    pending_review: int = 0
    completed: int = 0
    failed: int = 0
    cancelled: int = 0

class Project(BaseModel):
    """项目模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    path: str
    createdAt: str = Field(default_factory=lambda: datetime.now().isoformat())
    taskStats: Optional[TaskStats] = None
```

**操作文件**：`backend/app/models/project.py`（新建）

---

## T-03 创建任务模型和枚举

创建 `backend/app/models/task.py` 文件，定义 `Task` 模型及 `TaskType`、`TaskStatus` 枚举。

```python
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import uuid

class TaskType(str, Enum):
    FEATURE = "feature"
    BUG = "bug"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task(BaseModel):
    """任务模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    projectId: str
    type: TaskType
    title: str
    description: str
    module: str
    status: TaskStatus = TaskStatus.PENDING
    acceptanceCriteria: List[str] = []
    branch: Optional[str] = None
    worktreePath: Optional[str] = None
    bugReportPath: Optional[str] = None
    createdAt: str = Field(default_factory=lambda: datetime.now().isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.now().isoformat())
```

**操作文件**：`backend/app/models/task.py`（新建）

---

## T-04 创建日志模型和枚举

创建 `backend/app/models/log.py` 文件，定义 `LogEntry` 模型及 `LogStream` 枚举。

```python
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class LogStream(str, Enum):
    STDOUT = "stdout"
    STDERR = "stderr"

class LogEntry(BaseModel):
    """日志条目模型"""
    ts: str = Field(default_factory=lambda: datetime.now().isoformat())
    stream: LogStream = LogStream.STDOUT
    line: str
```

**操作文件**：`backend/app/models/log.py`（新建）

---

## T-05 统一导出所有模型

在 `backend/app/models/__init__.py` 中导出所有模型和枚举。

```python
from .project import Project, TaskStats
from .task import Task, TaskType, TaskStatus
from .log import LogEntry, LogStream

__all__ = [
    "Project",
    "TaskStats",
    "Task",
    "TaskType",
    "TaskStatus",
    "LogEntry",
    "LogStream"
]
```

**操作文件**：`backend/app/models/__init__.py`（修改）

---

## T-06 验证模型可序列化

在 `backend/app/models/__init__.py` 末尾添加验证代码（可选，仅用于开发时验证）：

```python
# 验证模型可正常序列化（开发阶段验证用）
if __name__ == "__main__":
    # 测试 Project 序列化
    project = Project(name="test", path="/tmp/test")
    print(project.model_dump())

    # 测试 Task 枚举
    print(TaskType.FEATURE.value)
    print(TaskStatus.PENDING.value)

    # 测试 LogEntry 反序列化
    log_data = {"ts": "2026-02-27T10:00:00", "stream": "stdout", "line": "test"}
    log = LogEntry.model_validate(log_data)
    print(log)
```

执行 `python -m app.models` 验证无报错。

**操作文件**：`backend/app/models/__init__.py`（修改）
