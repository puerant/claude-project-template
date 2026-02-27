from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.models import Task, TaskType, TaskStatus

router = APIRouter(prefix="/api", tags=["任务"])

project_service = ProjectService()
task_service = TaskService()


@router.get("/projects/{project_id}/tasks", response_model=list)
async def list_project_tasks(
    project_id: str,
    status: Optional[TaskStatus] = Query(None),
    task_type: Optional[TaskType] = Query(None),
):
    """获取项目的任务列表"""
    return task_service.list_tasks_filtered(project_id, status, task_type)


@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """获取任务详情"""
    projects = project_service.list_projects()

    for project in projects:
        task = task_service.get_task(project.id, task_id)
        if task:
            return task

    raise HTTPException(
        status_code=404, detail={"code": 40401, "message": "任务不存在"}
    )


@router.post("/tasks/{task_id}/cancel", response_model=Task)
async def cancel_task(task_id: str):
    """取消任务"""
    projects = project_service.list_projects()

    for project in projects:
        task = task_service.get_task(project.id, task_id)
        if task:
            return task_service.cancel_task(project.id, task_id)

    raise HTTPException(
        status_code=404, detail={"code": 40401, "message": "任务不存在"}
    )


@router.post("/tasks/{task_id}/reset", response_model=Task)
async def reset_task(task_id: str):
    """重置任务"""
    projects = project_service.list_projects()

    for project in projects:
        task = task_service.get_task(project.id, task_id)
        if task:
            return task_service.reset_task(project.id, task_id)

    raise HTTPException(
        status_code=404, detail={"code": 40401, "message": "任务不存在"}
    )


@router.post("/projects/{project_id}/sync")
async def sync_tasks(project_id: str):
    """同步任务清单"""
    projects = project_service.list_projects()
    project = next((p for p in projects if p.id == project_id), None)

    if not project:
        raise HTTPException(
            status_code=404, detail={"code": 40401, "message": "项目不存在"}
        )

    result = task_service.sync_tasks(project_id, project.path)
    return result
