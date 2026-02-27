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
