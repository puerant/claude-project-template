from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.services.project_service import ProjectService
from app.models import Project

router = APIRouter(prefix="/api/projects", tags=["项目"])

project_service = ProjectService()


class CreateProjectRequest(BaseModel):
    """创建项目请求"""

    name: str
    path: str


@router.get("", response_model=List[Project])
async def list_projects():
    """获取项目列表"""
    return project_service.list_projects()


@router.post("", response_model=Project)
async def create_project(req: CreateProjectRequest):
    """创建项目"""
    return project_service.add_project(req.name, req.path)


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """删除项目"""
    project_service.delete_project(project_id)
    return {"message": "项目已删除"}
