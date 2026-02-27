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
