# 原子任务：任务清单解析模块

> 任务编号：M2-T02

---

## T-01 创建任务解析服务

创建 `backend/app/services/task_parser.py`，定义 `TaskParser` 类，实现任务清单解析逻辑。

```python
from pathlib import Path
from typing import List
from app.models import Task, TaskType, TaskStatus


class TaskParser:
    """任务清单解析器"""

    def parse(self, project_path: str) -> List[Task]:
        """解析任务清单文件，返回任务列表"""
        task_list_file = Path(project_path) / "docs/开发文档/任务清单.md"

        if not task_list_file.exists():
            raise FileNotFoundError("任务清单文件不存在")

        content = task_list_file.read_text(encoding='utf-8')
        return self._parse_content(content, project_path)

    def _parse_content(self, content: str, project_path: str) -> List[Task]:
        """解析任务清单内容"""
        # 按 ## 分割任务块
        blocks = content.split('## ')

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
        lines = block.split('\n')
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
        # 这里先使用一个默认值
        from uuid import uuid4
        project_id = str(uuid4())

        return Task(
            projectId=project_id,
            type=task_type,
            title=title,
            description=description,
            module=module,
            acceptanceCriteria=acceptance_criteria
        )

    def _detect_type(self, title: str) -> TaskType:
        """从标题中检测任务类型"""
        title_lower = title.lower()
        if '[bug]' in title_lower or '缺陷' in title:
            return TaskType.BUG
        return TaskType.FEATURE

    def _extract_title(self, line: str) -> str:
        """从标题行提取任务标题"""
        # 移除类型标记
        line = line.replace('[feature]', '').replace('[bug]', '')
        line = line.replace('[缺陷]', '').replace('[功能]', '')
        # 移除编号如 T-01
        import re
        line = re.sub(r'T-\d+\s*', '', line)
        return line.strip()

    def _extract_field(self, content: str, field_name: str) -> str:
        """提取指定字段"""
        pattern = rf'\*\*{field_name}\*\*[:：]\s*(.+?)(?:\n|$)'
        import re
        match = re.search(pattern, content)
        return match.group(1).strip() if match else ""

    def _extract_description(self, content: str) -> str:
        """提取任务描述"""
        # 查找 ## 描述段落
        import re
        match = re.search(r'## 描述\s*\n+(.+?)(?=##|$)', content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_acceptance_criteria(self, content: str) -> List[str]:
        """提取验收标准列表"""
        import re
        # 查找验收标准部分
        match = re.search(r'## 验收标准|### 验收标准|验收标准[:：]\s*\n(.+?)(?=##|$)', content, re.DOTALL)
        if not match:
            return []

        criteria_text = match.group(1)
        # 提取列表项
        lines = criteria_text.split('\n')
        criteria = []
        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                criteria.append(line[2:].strip())

        return criteria
```

**操作文件**：`backend/app/services/task_parser.py`（新建）

---

## T-02 添加任务存储服务

创建 `backend/app/services/task_service.py`，定义 `TaskService` 类，实现任务的存储和合并逻辑。

```python
from pathlib import Path
from typing import List, Optional
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
            "total": len(merged_tasks)
        }
```

**操作文件**：`backend/app/services/task_service.py`（新建）

---

## T-03 更新 ProjectService 添加 taskStats

在 `ProjectService` 中添加计算 taskStats 的方法。

```python
from app.services.task_service import TaskService

class ProjectService:
    # ... 现有代码 ...

    def __init__(self, data_dir: str = "data"):
        self.projects_file = Path(data_dir) / "projects.json"
        self.task_service = TaskService(data_dir)

    def list_projects(self) -> List[Project]:
        """获取所有项目列表"""
        projects_data = read_json(str(self.projects_file), default=[])
        projects = []
        for p_data in projects_data:
            # 添加 taskStats
            tasks = self.task_service.list_tasks(p_data['id'])
            task_stats = self._calculate_stats(tasks)
            p_data['taskStats'] = task_stats
            projects.append(Project(**p_data))
        return projects

    def _calculate_stats(self, tasks: List[Task]) -> dict:
        """计算任务统计"""
        from app.models import TaskStatus
        stats = {
            "total": len(tasks),
            "pending": 0,
            "in_progress": 0,
            "pending_review": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0
        }

        for task in tasks:
            status = task.status.value if isinstance(task.status, TaskStatus) else str(task.status)
            if status in stats:
                stats[status] += 1

        return stats
```

**操作文件**：`backend/app/services/project_service.py`（修改）

---

## T-04 创建任务路由

创建 `backend/app/routers/task.py`，实现任务相关的 API 路由。

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.project_service import ProjectService
from app.services.task_service import TaskService

router = APIRouter(prefix="/api/projects", tags=["任务"])

project_service = ProjectService()
task_service = TaskService()


@router.post("/{project_id}/sync")
async def sync_tasks(project_id: str):
    """同步任务清单"""
    # 获取项目信息
    projects = project_service.list_projects()
    project = next((p for p in projects if p.id == project_id), None)

    if not project:
        raise HTTPException(status_code=404, detail={"code": 40401, "message": "项目不存在"})

    # 同步任务
    result = task_service.sync_tasks(project_id, project.path)
    return result
```

**操作文件**：`backend/app/routers/task.py`（新建）

---

## T-05 注册任务路由

在 `backend/app/main.py` 中注册任务路由。

```python
from app.routers import project, task

def create_app() -> FastAPI:
    # ... 现有代码 ...

    # 注册路由
    app.include_router(project.router)
    app.include_router(task.router)

    return app
```

**操作文件**：`backend/app/main.py`（修改）

---

## T-06 验证 API

启动服务并测试 API。

```bash
cd backend
python main.py
```

另开终端测试：

```bash
# 同步任务清单
curl -X POST http://localhost:8765/api/projects/{project-id}/sync
```

**操作文件**：无（验证步骤）
