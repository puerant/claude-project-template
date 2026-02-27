# 原子任务：Git 服务模块

> 任务编号：M2-T04

---

## T-01 创建 Git 服务

创建 `backend/app/services/git_service.py`，定义 `GitService` 类。

```python
from pathlib import Path
import subprocess
from typing import Tuple


class GitService:
    """Git 服务封装"""

    def create_branch(self, repo_path: str, branch_name: str, base: str = "dev") -> None:
        """从指定分支切出新分支"""
        result = subprocess.run(
            ["git", "-C", repo_path, "checkout", base, "-b", branch_name],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise Exception(f"创建分支失败: {stderr}")

    def create_worktree(self, repo_path: str, worktree_path: str, branch_name: str) -> None:
        """创建 git worktree"""
        result = subprocess.run(
            ["git", "worktree", "add", worktree_path, "-b", branch_name],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise Exception(f"创建 worktree 失败: {stderr}")

    def remove_worktree(self, repo_path: str, worktree_path: str) -> None:
        """删除 git worktree"""
        result = subprocess.run(
            ["git", "worktree", "remove", worktree_path],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise Exception(f"删除 worktree 失败: {stderr}")

    def commit_and_push(self, worktree_path: str, message: str) -> Tuple[str, str]:
        """在 worktree 中提交并推送代码"""
        # 提交
        result = subprocess.run(
            ["git", "-C", worktree_path, "commit", "-m", message],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise Exception(f"提交失败: {stderr}")

        # 获取提交哈希
        result = subprocess.run(
            ["git", "-C", worktree_path, "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
        )
        commit_hash = result.stdout.strip()

        # 推送
        result = subprocess.run(
            ["git", "push", "origin", branch_name],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise Exception(f"推送失败: {stderr}")

        return commit_hash, branch_name

    def execute_git(self, repo_path: str, command: list[str]) -> str:
        """执行 git 命令并捕获输出"""
        result = subprocess.run(
            ["git", "-C", repo_path] + command,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise Exception(f"执行 git 命令失败: {stderr}")
        return result.stdout.strip()
```

**操作文件**：`backend/app/services/git_service.py`（新建）

---

## T-02 添加异常类

在 `backend/app/core/exceptions.py` 中添加 Git 相关异常。

```python
class GitCommandError(Exception):
    """Git 命令执行失败异常"""
    pass


class GitError(HTTPException):
    """Git 操作失败错误 (50003)"""

    def __init__(self, detail: str = "Git 操作失败"):
        super().__init__(
            status_code=500, detail={"code": 50003, "message": detail}
        )
```

**操作文件**：`backend/app/core/exceptions.py`（修改）

---

## T-03 更新 Git 服务使用异常

修改 `GitService` 的方法，使用自定义异常。

```python
from app.core.exceptions import GitCommandError, GitError

class GitService:
    # ... 现有代码 ...

    def create_branch(self, repo_path: str, branch_name: str, base: str = "dev") -> None:
        """从指定分支切出新分支"""
        try:
            result = subprocess.run(
                ["git", "-C", repo_path, "checkout", base, "-b", branch_name],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                raise GitError(f"创建分支失败: {stderr}")
        except Exception as e:
            raise GitCommandError(f"创建分支异常: {str(e)}")

    def create_worktree(self, repo_path: str, worktree_path: str, branch_name: str) -> None:
        """创建 git worktree"""
        try:
            result = subprocess.run(
                ["git", "worktree", "add", worktree_path, "-b", branch_name],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                raise GitError(f"创建 worktree 失败: {stderr}")
        except Exception as e:
            raise GitCommandError(f"创建 worktree 异常: {str(e)}")

    def remove_worktree(self, repo_path: str, worktree_path: str) -> None:
        """删除 git worktree"""
        try:
            result = subprocess.run(
                ["git", "worktree", "remove", worktree_path],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                raise GitError(f"删除 worktree 失败: {stderr}")
        except Exception as e:
            raise GitCommandError(f"删除 worktree 异常: {str(e)}")

    def commit_and_push(self, worktree_path: str, message: str) -> Tuple[str, str]:
        """在 worktree 中提交并推送代码"""
        try:
            # 提交
            result = subprocess.run(
                ["git", "-C", worktree_path, "commit", "-m", message],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                raise GitError(f"提交失败: {stderr}")

            # 获取提交哈希和分支名
            result = subprocess.run(
                ["git", "-C", worktree_path, "rev-parse", "HEAD", "--abbrev-ref"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise GitCommandError(f"获取分支名失败")
            branch_name = result.stdout.strip()

            # 推送
            result = subprocess.run(
                ["git", "push", "origin", branch_name],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                raise GitError(f"推送失败: {stderr}")

            return commit_hash, branch_name
        except Exception as e:
            raise GitCommandError(f"提交推送异常: {str(e)}")
```

**操作文件**：`backend/app/services/git_service.py`（修改）

---

## T-04 验证 Git 服务

验证 Git 命令可以正常执行。

```bash
cd backend
python -c "
from app.services.git_service import GitService

service = GitService()

# 测试获取当前分支（应该捕获异常）
try:
    branch = service.execute_git('.', ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    print(f'当前分支: {branch}')
except Exception as e:
    print(f'异常: {e}')
"
```

**操作文件**：无（验证步骤）
