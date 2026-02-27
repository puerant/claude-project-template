from pathlib import Path
from subprocess import run
from typing import Tuple
from app.core.exceptions import GitCommandError, GitError


class GitService:
    """Git 服务封装"""

    def create_branch(self, repo_path: str, branch_name: str, base: str = "dev") -> None:
        """从指定分支切出新分支"""
        try:
            result = run(
                ["git", "-C", repo_path, "checkout", base, "-b", branch_name],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                raise GitCommandError(f"创建分支失败: {stderr}")
        except Exception as e:
            raise GitCommandError(f"创建分支异常: {str(e)}")

    def create_worktree(self, repo_path: str, worktree_path: str, branch_name: str) -> None:
        """创建 git worktree"""
        try:
            result = run(
                ["git", "worktree", "add", worktree_path, "-b", branch_name],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                raise GitCommandError(f"创建 worktree 失败: {stderr}")
        except Exception as e:
            raise GitCommandError(f"创建 worktree 异常: {str(e)}")

    def remove_worktree(self, repo_path: str, worktree_path: str) -> None:
        """删除 git worktree"""
        try:
            result = run(
                ["git", "worktree", "remove", worktree_path],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                raise GitCommandError(f"删除 worktree 失败: {stderr}")
        except Exception as e:
            raise GitCommandError(f"删除 worktree 异常: {str(e)}")

    def commit_and_push(self, worktree_path: str, message: str) -> Tuple[str, str]:
        """在 worktree 中提交并推送代码"""
        try:
            # 提交
            result = run(
                ["git", "-C", worktree_path, "commit", "-m", message],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                raise GitCommandError(f"提交失败: {stderr}")

            # 获取提交哈希和分支名
            result = run(
                ["git", "-C", worktree_path, "rev-parse", "HEAD", "--abbrev-ref"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise GitCommandError("获取分支名失败")

            branch_name = result.stdout.strip()

            # 推送
            result = run(
                ["git", "push", "origin", branch_name],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                raise GitCommandError(f"推送失败: {stderr}")

            return result.stdout.strip(), branch_name
        except Exception as e:
            raise GitCommandError(f"提交推送异常: {str(e)}")

    def execute_git(self, repo_path: str, command: list[str]) -> str:
        """执行 git 命令并捕获输出"""
        try:
            result = run(
                ["git", "-C", repo_path] + command,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                raise GitCommandError(f"执行 git 命令失败: {stderr}")
            return result.stdout.strip()
        except Exception as e:
            raise GitCommandError(f"执行 git 命令异常: {str(e)}")
