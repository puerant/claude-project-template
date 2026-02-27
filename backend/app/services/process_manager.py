import subprocess
from typing import Dict
from app.core.exceptions import ProcessError, GitError
from app.services.git_service import GitService


class ProcessManager:
    """进程管理器"""

    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.git_service = GitService()

    def start(self, task_id: str, worktree_path: str, prompt: str) -> None:
        """启动任务执行进程"""
        try:
            if task_id in self.processes:
                raise ValueError(f"任务 {task_id} 已在运行中")

            # 启动 claude --print <prompt>
            process = subprocess.Popen(
                ["claude", "--print", prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=worktree_path,
                text=True,
            )

            self.processes[task_id] = process
            return None
        except ValueError as e:
            raise ProcessError(str(e))
        except Exception as e:
            raise ProcessError(f"启动进程异常: {str(e)}")

    def stop(self, task_id: str) -> None:
        """停止任务执行进程"""
        try:
            if task_id not in self.processes:
                raise ValueError(f"任务 {task_id} 未在运行中")

            process = self.processes[task_id]
            process.terminate()

            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

            del self.processes[task_id]
        except ValueError as e:
            raise ProcessError(str(e))
        except Exception as e:
            raise ProcessError(f"停止进程异常: {str(e)}")

    def get_process(self, task_id: str) -> subprocess.Popen | None:
        """获取任务进程对象"""
        return self.processes.get(task_id)
