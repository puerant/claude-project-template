from fastapi import APIRouter
from typing import List
from app.services.bug_report_service import BugReportService
from app.services.project_service import ProjectService
from app.models import BugReport

router = APIRouter(prefix="/api/projects", tags=["bug"])

bug_report_service = BugReportService()
project_service = ProjectService()


@router.get("/{projectId}/bugs", response_model=List[BugReport])
async def list_bug_reports(projectId: str):
    """获取项目的 Bug 报告列表"""
    project = project_service.get_project(projectId)
    return bug_report_service.list_bug_reports(project.path)
