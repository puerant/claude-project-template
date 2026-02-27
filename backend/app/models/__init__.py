from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid

class TaskStats(BaseModel):
    total: int = 0
    pending: int = 0
    in_progress: int = 0
    pending_review: int = 0
    completed: int = 0
    failed: int = 0
    cancelled: int = 0

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    path: str
    createdAt: str = Field(default_factory=lambda: datetime.now().isoformat())
    taskStats: Optional[TaskStats] = None

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

class LogStream(str, Enum):
    STDOUT = "stdout"
    STDERR = "stderr"

class LogEntry(BaseModel):
    ts: str = Field(default_factory=lambda: datetime.now().isoformat())
    stream: LogStream = LogStream.STDOUT
    line: str

__all__ = [
    "Project", "TaskStats", "Task", "TaskType", "TaskStatus", "LogEntry", "LogStream"
]

if __name__ == "__main__":
    project = Project(name="test", path="/tmp/test")
    print("Project:", project.model_dump())
    print("TaskType.FEATURE:", TaskType.FEATURE.value)
    print("TaskStatus.PENDING:", TaskStatus.PENDING.value)
    log_data = {"ts": "2026-02-27T10:00:00", "stream": "stdout", "line": "test"}
    log = LogEntry.model_validate(log_data)
    print("LogEntry:", log)
    print("验证通过！")
