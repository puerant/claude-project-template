# 技术方案：Pydantic 数据模型定义

> 任务编号：M1-T02

---

## 架构设计

### 1.1 模型文件组织

```
backend/app/models/
├── __init__.py     # 导出所有模型和枚举
├── project.py      # Project, TaskStats
├── task.py         # Task, TaskType, TaskStatus
└── log.py          # LogEntry, LogStream
```

### 1.2 模块职责

| 文件 | 职责 |
| ---- | ---- |
| `models/__init__.py` | 统一导出接口，方便路由层导入 |
| `models/project.py` | 项目相关模型定义 |
| `models/task.py` | 任务相关模型和枚举定义 |
| `models/log.py` | 日志相关模型和枚举定义 |

---

## 数据结构

### 2.1 项目模型

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

### 2.2 任务模型

```python
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

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

### 2.3 日志模型

```python
from enum import Enum
from pydantic import BaseModel
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

---

## 接口定义

本任务不涉及 HTTP 接口，仅定义数据模型供后续路由使用。

---

## 技术选型

| 技术点 | 选型 | 说明 |
| ------- | ---- | ---- |
| 数据验证 | Pydantic v2 | 类型安全、自动文档生成 |
| 时间格式 | ISO 8601 字符串 | 与前端 TypeScript 保持一致 |
| 枚举实现 | Python Enum | 类型安全、支持序列化 |
| UUID 生成 | Python uuid.uuid4() | 标准唯一标识 |
