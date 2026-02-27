# 原子任务：Prompt 构建器

> 任务编号：M2-T05

---

## T-01 创建 Prompt 构建服务

创建 `backend/app/services/prompt_service.py`，定义 `PromptService` 类。

```python
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
```

**操作文件**：`backend/app/services/prompt_service.py`（新建）

---

## T-02 验证 Prompt 构建服务

验证 Prompt 构建的正确性。

```bash
cd backend
python -c "
from app.services.prompt_service import PromptService
from app.models import Task, TaskType

service = PromptService()

# 测试 feature 类型任务
task = Task(
    id='test-123',
    projectId='test-project',
    type=TaskType.FEATURE,
    title='测试功能',
    description='这是一个测试功能的描述',
    module='测试模块',
    acceptanceCriteria=['标准1', '标准2'],
    branch='feat/test-branch',
    worktreePath='.worktrees/test',
)

prompt = service.build_prompt(task, '/tmp/test')
print(prompt)
"
```

**操作文件**：无（验证步骤）
