from pathlib import Path
from app.models import Task, TaskType


class PromptService:
    """Prompt 构建服务"""

    def build_prompt(self, task: Task, project_path: str) -> str:
        """构建 Claude Code 的完整 Prompt"""
        prompt_lines = []

        # 任务类型和标题
        type_label = "功能" if task.type == TaskType.FEATURE else "缺陷"
        prompt_lines.append(f"# {type_label}: {task.title}")

        # 模块
        if task.module:
            prompt_lines.append(f"\n**模块**：{task.module}")

        # 描述
        if task.description:
            prompt_lines.append(f"\n**描述**\n{task.description}")

        # 验收标准
        if task.acceptanceCriteria:
            prompt_lines.append(f"\n**验收标准**")
            for i, criteria in enumerate(task.acceptanceCriteria, 1):
                prompt_lines.append(f"{i+1}. {criteria}")

        # 分支和 worktree 信息
        if task.branch:
            prompt_lines.append(f"\n**分支名称**：{task.branch}")
        if task.worktreePath:
            prompt_lines.append(f"\n**Worktree 路径**：{task.worktreePath}")

        # 经验总结
        experience_file = Path(project_path) / "docs/开发文档/经验总结.md"
        if experience_file.exists():
            with open(experience_file, 'r', encoding='utf-8') as f:
                experience = f.read()
            if experience.strip():
                prompt_lines.append(f"\n**经验总结**\n{experience}")

        # 结果格式要求
        prompt_lines.append("\n\n请按照以下格式返回结果：")
        prompt_lines.append("SUCCESS 或 FAILURE: <失败原因>")
        prompt_lines.append("\n")

        return "\n".join(prompt_lines)
