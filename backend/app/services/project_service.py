from pathlib import Path
from typing import List
from app.core import read_json, write_json
from app.core.exceptions import (
    PathNotFoundError,
    TaskListNotFoundError,
    DuplicatePathError,
    ProjectNotFoundError,
)
from app.models import Project, TaskStats, Task, TaskStatus
from app.services.task_service import TaskService


class ProjectService:
    """项目管理服务"""

    def __init__(self, data_dir: str = "data"):
        self.projects_file = Path(data_dir) / "projects.json"
        self.task_service = TaskService(data_dir)

    def list_projects(self) -> List[Project]:
        """获取所有项目列表"""
        projects_data = read_json(str(self.projects_file), default=[])
        projects = []
        for p_data in projects_data:
            # 添加 taskStats
            tasks = self.task_service.list_tasks(p_data["id"])
            task_stats = self._calculate_stats(tasks)
            p_data["taskStats"] = task_stats
            projects.append(Project(**p_data))
        return projects

    def _calculate_stats(self, tasks: List[Task]) -> dict:
        """计算任务统计"""
        stats = {
            "total": len(tasks),
            "pending": 0,
            "in_progress": 0,
            "pending_review": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
        }

        for task in tasks:
            status = (
                task.status.value
                if isinstance(task.status, TaskStatus)
                else str(task.status)
            )
            if status in stats:
                stats[status] += 1

        return stats

    def save_projects(self, projects: List[Project]) -> None:
        """保存项目列表"""
        projects_data = [p.model_dump() for p in projects]
        write_json(str(self.projects_file), projects_data)

    def add_project(self, name: str, path: str) -> Project:
        """添加新项目"""
        project_path = Path(path)

        if not project_path.exists():
            raise PathNotFoundError()

        task_list_file = project_path / "docs/开发文档/任务清单.md"
        if not task_list_file.exists():
            raise TaskListNotFoundError()

        projects = self.list_projects()
        for p in projects:
            if p.path == path:
                raise DuplicatePathError()

        new_project = Project(name=name, path=path, taskStats=TaskStats())
        projects.append(new_project)
        self.save_projects(projects)

        return new_project

    def get_project(self, project_id: str) -> Project:
        """根据 ID 获取项目"""
        projects = self.list_projects()
        for p in projects:
            if p.id == project_id:
                return p
        raise ProjectNotFoundError()

    def delete_project(self, project_id: str) -> None:
        """删除项目"""
        projects = self.list_projects()
        original_count = len(projects)
        projects = [p for p in projects if p.id != project_id]

        if len(projects) == original_count:
            raise ProjectNotFoundError()

        self.save_projects(projects)
