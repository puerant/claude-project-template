from pathlib import Path
from typing import List, Optional
from app.core import read_json, write_json
from app.models import Task, TaskStatus, TaskType
from app.services.task_parser import TaskParser
from app.services.execution_service import ExecutionService
from app.core.exceptions import InvalidStatusTransitionError


class TaskService:
    """任务管理服务"""

    def __init__(self, data_dir: str = "data"):
        self.tasks_dir = Path(data_dir) / "tasks"
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.parser = TaskParser()
        self.execution_service = ExecutionService()

    def get_tasks_file(self, project_id: str) -> Path:
        """获取项目的任务文件路径"""
        return self.tasks_dir / f"{project_id}.json"

    def list_tasks(self, project_id: str) -> List[Task]:
        """获取项目的所有任务"""
        tasks_file = self.get_tasks_file(project_id)
        tasks_data = read_json(str(tasks_file), default=[])
        return [Task(**t) for t in tasks_data]

    def list_tasks_filtered(
        self,
        project_id: str,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None,
    ) -> List[Task]:
        """获取项目的任务列表（支持过滤）"""
        all_tasks = self.list_tasks(project_id)

        filtered = all_tasks
        if status:
            filtered = [t for t in filtered if t.status == status]
        if task_type:
            filtered = [t for t in filtered if t.type == task_type]

        # 按 updatedAt 降序排列
        filtered.sort(key=lambda t: t.updatedAt, reverse=True)
        return filtered

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

    def get_task(self, project_id: str, task_id: str) -> Task | None:
        """获取指定任务详情"""
        tasks = self.list_tasks(project_id)
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def cancel_task(self, project_id: str, task_id: str) -> Task:
        """取消任务"""
        tasks = self.list_tasks(project_id)
        for i, task in enumerate(tasks):
            if task.id == task_id:
                if task.status not in [
                    TaskStatus.PENDING,
                    TaskStatus.IN_PROGRESS,
                    TaskStatus.PENDING_REVIEW,
                ]:
                    raise InvalidStatusTransitionError()

                task.status = TaskStatus.CANCELLED
                tasks[i] = task
                break

        self.save_tasks(project_id, tasks)
        return task

    def reset_task(self, project_id: str, task_id: str) -> Task:
        """重置任务"""
        tasks = self.list_tasks(project_id)
        for i, task in enumerate(tasks):
            if task.id == task_id:
                if task.status != TaskStatus.FAILED:
                    raise InvalidStatusTransitionError()

                task.status = TaskStatus.PENDING
                task.branch = None
                task.worktreePath = None
                tasks[i] = task
                break

        self.save_tasks(project_id, tasks)
        return task

    def get_task_by_id(self, task_id: str) -> tuple[Task, str]:
        """
        通过 task_id 获取任务（遍历所有项目）
        Returns:
            (task, project_id): 任务和所属项目 ID
        Raises:
            ValueError: 任务不存在
        """
        # 遍历所有任务文件
        for tasks_file in self.tasks_dir.glob("*.json"):
            tasks = read_json(str(tasks_file), default=[])
            for task_data in tasks:
                if task_data["id"] == task_id:
                    return Task(**task_data), tasks_file.stem
        raise ValueError(f"任务 {task_id} 不存在")

    def execute_task(self, project_id: str, task_id: str) -> Task:
        """执行任务"""
        # 获取任务
        task = self.get_task(project_id, task_id)
        if task is None:
            raise ValueError(f"任务 {task_id} 不存在")

        # 获取项目路径
        from app.services.project_service import ProjectService
        project_service = ProjectService()
        project = project_service.get_project(project_id)
        project_path = project.path

        # 执行任务
        updated_task = self.execution_service.execute(task, project_path)

        # 保存任务
        tasks = self.list_tasks(project_id)
        for i, t in enumerate(tasks):
            if t.id == task_id:
                tasks[i] = updated_task
                break
        self.save_tasks(project_id, tasks)

        return updated_task