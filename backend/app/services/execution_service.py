from pathlib import Path
from app.models import Task, TaskStatus
from app.services.git_service import GitService
from app.services.process_manager import ProcessManager
from app.services.prompt_service import PromptService
from app.services.output_parser import OutputParser
from app.core.file_utils import read_json, write_json
from app.core.exceptions import InvalidStatusTransitionError


class ExecutionService:
    """任务执行引擎"""

    def __init__(self):
        self.git_service = GitService()
        self.process_manager = ProcessManager()
        self.prompt_service = PromptService()
        self.output_parser = OutputParser()
        self.data_dir = Path(__file__).parent.parent.parent / "data"

    def execute(self, task: Task, project_path: str) -> Task:
        """
        执行任务流程：
        1. 校验状态（必须是 pending）
        2. 创建分支
        3. 创建 worktree
        4. 构建 Prompt
        5. 启动进程
        6. 更新状态为 in_progress
        """
        # 校验状态
        if task.status != TaskStatus.PENDING:
            raise InvalidStatusTransitionError()

        # 生成分支名和 worktree 路径
        task_id = task.id
        branch = f"feat/{task_id}"
        worktree_path = str(self.data_dir / "worktrees" / task_id)

        # 创建分支
        self.git_service.create_branch(project_path, branch)

        # 创建 worktree
        self.git_service.create_worktree(project_path, worktree_path, branch)

        # 构建 Prompt
        prompt = self.prompt_service.build_prompt(task, project_path)

        # 启动进程
        self.process_manager.start(task_id, worktree_path, prompt)

        # 更新任务状态
        task.status = TaskStatus.IN_PROGRESS
        task.branch = branch
        task.worktreePath = worktree_path

        return task

    def cancel(self, task: Task) -> Task:
        """
        取消任务：
        1. 终止进程
        2. 删除 worktree
        3. 更新状态为 cancelled
        """
        if task.worktreePath:
            # 终止进程
            try:
                self.process_manager.stop(task.id)
            except Exception:
                pass

            # 删除 worktree
            try:
                self.git_service.remove_worktree(".", task.worktreePath)
            except Exception:
                pass

        # 更新状态
        task.status = TaskStatus.CANCELLED
        task.branch = None
        task.worktreePath = None

        return task

    def reset(self, task: Task) -> Task:
        """
        重置失败任务：
        1. 删除 worktree
        2. 清空 branch 和 worktreePath
        3. 更新状态为 pending
        """
        if task.worktreePath:
            # 删除 worktree
            try:
                self.git_service.remove_worktree(".", task.worktreePath)
            except Exception:
                pass

        # 更新状态
        task.status = TaskStatus.PENDING
        task.branch = None
        task.worktreePath = None

        return task
