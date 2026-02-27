from fastapi import APIRouter, HTTPException
from app.services.project_service import ProjectService
from app.services.task_service import TaskService

router = APIRouter(prefix="/api/projects", tags=["任务"])

project_service = ProjectService()
task_service = TaskService()


@router.post("/{project_id}/sync")
async def sync_tasks(project_id: str):
    """同步任务清单"""
    # 获取项目信息
    projects = project_service.list_projects()
    project = next((p for p in projects if p.id == project_id), None)

    if not project:
        raise HTTPException(
            status_code=404, detail={"code": 40401, "message": "项目不存在"}
        )

    # 同步任务
    result = task_service.sync_tasks(project_id, project.path)
    return result
