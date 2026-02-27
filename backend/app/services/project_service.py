from pathlib import Path
from typing import List
from app.core import read_json, write_json
from app.core.exceptions import (
    PathNotFoundError,
    TaskListNotFoundError,
    DuplicatePathError,
    ProjectNotFoundError,
)
from app.models import Project, TaskStats


class ProjectService:
    """项目管理服务"""

    def __init__(self, data_dir: str = "data"):
        self.projects_file = Path(data_dir) / "projects.json"

    def list_projects(self) -> List[Project]:
        """获取所有项目列表"""
        projects = read_json(str(self.projects_file), default=[])
        return [Project(**p) for p in projects]

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

    def delete_project(self, project_id: str) -> None:
        """删除项目"""
        projects = self.list_projects()
        original_count = len(projects)
        projects = [p for p in projects if p.id != project_id]

        if len(projects) == original_count:
            raise ProjectNotFoundError()

        self.save_projects(projects)
