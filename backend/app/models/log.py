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
