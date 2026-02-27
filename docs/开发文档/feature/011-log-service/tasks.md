# 原子任务：日志服务模块

> 任务编号：M2-T08

---

## T-01 创建日志服务

创建 `backend/app/services/log_service.py`，定义 `LogService` 类。

```python
from pathlib import Path
from datetime import datetime
from app.models import LogEntry, LogStream
from app.core.file_utils import read_json_lines, write_json_lines


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
```

**操作文件**：`backend/app/services/log_service.py`（新建）

---

## T-02 更新文件工具类

在 `backend/app/core/file_utils.py` 中添加读取 JSONL 文件的函数。

```python
def read_json_lines(path: str) -> list:
    """读取 JSONL 文件，每行一个 JSON 对象"""
    file_path = Path(path)
    if not file_path.exists():
        return []

    lines = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(json.loads(line))
    return lines
```

**操作文件**：`backend/app/core/file_utils.py`（修改）

---

## T-03 创建日志 API 路由

创建 `backend/app/routers/log.py`，实现日志查询和 SSE 流式推送的 API 端点。

```python
import asyncio
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from app.services.log_service import LogService
from app.services.process_manager import ProcessManager

router = APIRouter(prefix="/api/tasks", tags=["日志"])

log_service = LogService()
process_manager = ProcessManager()


@router.get("/{taskId}/logs")
async def get_logs(taskId: str):
    """获取任务历史日志"""
    logs = log_service.get_logs(taskId)
    return [log.model_dump() for log in logs]


@router.get("/{taskId}/logs/stream")
async def stream_logs(taskId: str):
    """实时推送任务日志（SSE）"""
    async def event_generator():
        # 检查进程是否在运行
        process = process_manager.get_process(taskId)

        if process is None:
            # 进程已结束，返回历史日志后关闭
            logs = log_service.get_logs(taskId)
            for log in logs:
                yield {
                    "event": "log",
                    "data": log.model_dump_json()
                }
            yield {"event": "done"}
            return

        # 进程运行中，实时推送
        while True:
            # 检查进程状态
            process = process_manager.get_process(taskId)
            if process is None:
                # 进程已退出
                logs = log_service.get_logs(taskId)
                for log in logs:
                    yield {
                        "event": "log",
                        "data": log.model_dump_json()
                    }
                yield {"event": "done"}
                break

            # 等待新日志（简单实现：每秒检查一次）
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
```

**操作文件**：`backend/app/routers/log.py`（新建）

---

## T-04 注册日志路由

在 `backend/app/main.py` 中注册日志路由。

```python
from app.routers import project, task, process, execution, log
```

**操作文件**：`backend/app/main.py`（修改）

---

## T-05 验证日志服务

验证日志服务功能是否正常工作。

```bash
cd backend
python -c "
from app.services.log_service import LogService

service = LogService()

# 测试追加日志
service.append_log('test-task', '测试日志行 1')
service.append_log('test-task', '测试日志行 2')

# 测试获取日志
logs = service.get_logs('test-task')
print(f'日志数量: {len(logs)}')
for log in logs:
    print(f'{log.ts} [{log.stream}] {log.line}')

# 测试清空日志
service.clear_logs('test-task')
logs_after = service.get_logs('test-task')
print(f'清空后日志数量: {len(logs_after)}')
"
```

**操作文件**：无（验证步骤）
