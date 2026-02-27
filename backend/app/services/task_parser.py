from pathlib import Path
from typing import List
from app.models import Task, TaskType, TaskStatus
import re
from uuid import uuid4


class TaskParser:
    """任务清单解析器"""

    def parse(self, project_path: str) -> List[Task]:
        """解析任务清单文件，返回任务列表"""
        task_list_file = Path(project_path) / "docs/开发文档/任务清单.md"

        if not task_list_file.exists():
            raise FileNotFoundError("任务清单文件不存在")

        content = task_list_file.read_text(encoding="utf-8")
        return self._parse_content(content, project_path)

    def _parse_content(self, content: str, project_path: str) -> List[Task]:
        """解析任务清单内容"""
        # 按 ## 分割任务块
        blocks = content.split("## ")

        tasks = []
        for block in blocks[1:]:  # 跳过第一个空块
            task = self._parse_block(block.strip(), project_path)
            if task:
                tasks.append(task)

        return tasks

    def _parse_block(self, block: str, project_path: str) -> Task | None:
        """解析单个任务块"""
        if not block:
            return None

        # 解析标题行
        lines = block.split("\n")
        title_line = lines[0].strip()

        # 识别任务类型
        task_type = self._detect_type(title_line)

        # 提取标题
        title = self._extract_title(title_line)

        # 提取模块
        module = self._extract_field(block, "模块")

        # 提取描述
        description = self._extract_description(block)

        # 提取验收标准
        acceptance_criteria = self._extract_acceptance_criteria(block)

        # 暂时用一个固定的 projectId，实际应该从参数传入
        project_id = str(uuid4())

        return Task(
            projectId=project_id,
            type=task_type,
            title=title,
            description=description,
            module=module,
            acceptanceCriteria=acceptance_criteria,
        )

    def _detect_type(self, title: str) -> TaskType:
        """从标题中检测任务类型"""
        title_lower = title.lower()
        if "[bug]" in title_lower or "缺陷" in title:
            return TaskType.BUG
        return TaskType.FEATURE

    def _extract_title(self, line: str) -> str:
        """从标题行提取任务标题"""
        # 移除类型标记
        line = line.replace("[feature]", "").replace("[bug]", "")
        line = line.replace("[缺陷]", "").replace("[功能]", "")
        # 移除编号如 T-01
        line = re.sub(r"T-\d+\s*", "", line)
        return line.strip()

    def _extract_field(self, content: str, field_name: str) -> str:
        """提取指定字段"""
        pattern = rf"\*\*{field_name}\*\*[:：]\s*(.+?)(?:\n|$)"
        match = re.search(pattern, content)
        return match.group(1).strip() if match else ""

    def _extract_description(self, content: str) -> str:
        """提取任务描述"""
        # 查找 ## 描述段落
        match = re.search(r"## 描述\s*\n+(.+?)(?=##|$)", content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_acceptance_criteria(self, content: str) -> List[str]:
        """提取验收标准列表"""
        # 查找验收标准部分
        match = re.search(
            r"## 验收标准|### 验收标准|验收标准[:：]\s*\n(.+?)(?=##|$)",
            content,
            re.DOTALL,
        )
        if not match:
            return []

        criteria_text = match.group(1)
        # 提取列表项
        lines = criteria_text.split("\n")
        criteria = []
        for line in lines:
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                criteria.append(line[2:].strip())

        return criteria
