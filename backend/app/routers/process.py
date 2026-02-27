from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.process_manager import ProcessManager

router = APIRouter(prefix="/api/tasks", tags=["进程"])

process_manager = ProcessManager()


class StartProcessRequest(BaseModel):
    """启动进程请求"""
    prompt: str
    task_id: str


class StopProcessRequest(BaseModel):
    """停止进程请求"""
    task_id: str


@router.post("/{task_id}/start", response_model=dict)
async def start_process(req: StartProcessRequest):
    """启动任务执行进程"""
    return process_manager.start(req.task_id, ".worktrees/" + req.task_id, req.prompt)


@router.post("/{task_id}/stop", response_model=dict)
async def stop_process(req: StopProcessRequest):
    """停止任务执行进程"""
    process_manager.stop(req.task_id)
    return {"message": "任务已停止"}
