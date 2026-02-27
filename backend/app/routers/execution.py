from fastapi import APIRouter
from app.services.task_service import TaskService

router = APIRouter(prefix="/api/tasks", tags=["执行"])

task_service = TaskService()


@router.post("/{taskId}/execute")
async def execute_task(taskId: str):
    """执行任务"""
    return task_service.execute_task(None, taskId)


@router.post("/{taskId}/cancel")
async def cancel_task(taskId: str):
    """取消任务"""
    task, project_id = task_service.get_task_by_id(taskId)
    return task_service.cancel_task(project_id, taskId)


@router.post("/{taskId}/reset")
async def reset_task(taskId: str):
    """重置任务"""
    task, project_id = task_service.get_task_by_id(taskId)
    return task_service.reset_task(project_id, taskId)
