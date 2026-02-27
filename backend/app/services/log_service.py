from pathlib import Path
from datetime import datetime
from app.models import LogEntry, LogStream
from app.core.file_utils import read_json_lines


class LogService:
    """日志服务"""

    def __init__(self, data_dir: str = "data"):
        self.logs_dir = Path(data_dir) / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def get_log_file(self, task_id: str) -> Path:
        """获取任务的日志文件路径"""
        return self.logs_dir / f"{task_id}.jsonl"

    def append_log(self, task_id: str, line: str, stream: LogStream = LogStream.STDOUT) -> None:
        """追加日志行"""
        log_entry = LogEntry(
            ts=datetime.now().isoformat(),
            stream=stream,
            line=line
        )
        log_file = self.get_log_file(task_id)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry.model_dump_json() + "\n")

    def get_logs(self, task_id: str) -> list[LogEntry]:
        """获取任务的所有日志"""
        log_file = self.get_log_file(task_id)
        if not log_file.exists():
            return []

        lines = read_json_lines(str(log_file))
        return [LogEntry(**line) for line in lines]

    def clear_logs(self, task_id: str) -> None:
        """清空任务日志"""
        log_file = self.get_log_file(task_id)
        if log_file.exists():
            log_file.unlink()
