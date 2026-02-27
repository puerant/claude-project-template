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
