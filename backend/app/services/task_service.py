from pathlib import Path
from typing import List
from app.core import read_json, write_json
from app.models import Task, TaskStatus
from app.services.task_parser import TaskParser


class TaskService:
    """任务管理服务"""

    def __init__(self, data_dir: str = "data"):
        self.tasks_dir = Path(data_dir) / "tasks"
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.parser = TaskParser()

    def get_tasks_file(self, project_id: str) -> Path:
        """获取项目的任务文件路径"""
        return self.tasks_dir / f"{project_id}.json"

    def list_tasks(self, project_id: str) -> List[Task]:
        """获取项目的所有任务"""
        tasks_file = self.get_tasks_file(project_id)
        tasks_data = read_json(str(tasks_file), default=[])
        return [Task(**t) for t in tasks_data]

    def save_tasks(self, project_id: str, tasks: List[Task]) -> None:
        """保存项目任务"""
        tasks_file = self.get_tasks_file(project_id)
        tasks_data = [t.model_dump() for t in tasks]
        write_json(str(tasks_file), tasks_data)

    def sync_tasks(self, project_id: str, project_path: str) -> dict:
        """同步任务：解析任务清单并合并到现有任务"""
        # 解析新任务
        new_tasks = self.parser.parse(project_path)

        # 更新 projectId
        for task in new_tasks:
            task.projectId = project_id

        # 获取现有任务
        existing_tasks = self.list_tasks(project_id)

        # 合并：保留现有任务的状态
        merged_tasks = []
        existing_map = {t.title: t for t in existing_tasks}

        added_count = 0
        unchanged_count = 0

        for new_task in new_tasks:
            if new_task.title in existing_map:
                # 已存在，保留状态
                existing_task = existing_map[new_task.title]
                new_task.status = existing_task.status
                new_task.id = existing_task.id
                new_task.createdAt = existing_task.createdAt
                new_task.updatedAt = existing_task.updatedAt
                unchanged_count += 1
            else:
                # 新任务
                added_count += 1

            merged_tasks.append(new_task)

        # 保存合并后的任务
        self.save_tasks(project_id, merged_tasks)

        return {
            "added": added_count,
            "unchanged": unchanged_count,
            "total": len(merged_tasks),
        }
