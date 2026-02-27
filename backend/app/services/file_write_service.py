from pathlib import Path
from datetime import datetime
from app.models import Task


class FileWriteService:
    """文件写入服务：向被管理项目写入文档"""

    def append_experience(self, project_path: str, task_title: str, failure_reason: str) -> None:
        """向被管理项目的经验总结.md 追加失败经验"""
        exp_file = Path(project_path) / "docs/开发文档/经验总结.md"
        exp_file.parent.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        content = f"""
---

## {date_str} {task_title}

**问题**：{failure_reason}

**原因**：（待分析）

**解决方案**：（待填写）
"""
        with open(exp_file, "a", encoding="utf-8") as f:
            f.write(content)

    def create_bug_report(self, project_path: str, task: Task, failed_criteria: list[str]) -> str:
        """
        在被管理项目的 docs/bug/ 目录生成 Bug 报告文件
        Returns:
            relative_path: Bug 报告相对于项目根目录的路径
        """
        bug_dir = Path(project_path) / "docs/bug"
        bug_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%Y-%m-%d %H:%M")

        short_desc = failed_criteria[0][:20] if failed_criteria else "测试失败"
        raw_name = f"{date_str}-{task.module}-{task.title[:10]}-{short_desc}.md"
        for ch in r'/\:*?"<>|':
            raw_name = raw_name.replace(ch, "-")
        filename = raw_name

        bug_file = bug_dir / filename

        acceptance_text = "\n".join(f"- {c}" for c in task.acceptanceCriteria)
        failed_text = "\n".join(f"- {c}" for c in failed_criteria)

        content = f"""# Bug 报告

- **时间**：{time_str}
- **模块**：{task.module}
- **功能**：{task.title}
- **任务 ID**：{task.id}
- **分支**：{task.branch or "未知"}

## 问题描述

{failed_text}

## 复现步骤

（待填写）

## 期望结果

{acceptance_text}

## 实际结果

（测试失败的实际现象）

## 状态

- [ ] 待修复
"""
        with open(bug_file, "w", encoding="utf-8") as f:
            f.write(content)

        return f"docs/bug/{filename}"

    def read_experience(self, project_path: str) -> str:
        """读取被管理项目经验总结.md 全文"""
        exp_file = Path(project_path) / "docs/开发文档/经验总结.md"
        if not exp_file.exists():
            return ""
        with open(exp_file, "r", encoding="utf-8") as f:
            return f.read()
