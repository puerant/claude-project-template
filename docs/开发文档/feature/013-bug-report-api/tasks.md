# 原子任务：Bug 报告列表接口

> 任务编号：M2-T10

---

## T-01 新增 BugReport 模型

在 `backend/app/models/__init__.py` 中新增 `BugReport` Pydantic 模型，并加入 `__all__`。

```python
class BugReport(BaseModel):
    filename: str
    relativePath: str
    taskId: str
    module: str
    feature: str
    description: str
    createdAt: str
```

**操作文件**：`backend/app/models/__init__.py`（修改）

---

## T-02 创建 BugReportService

创建 `backend/app/services/bug_report_service.py`，定义 `BugReportService` 类。

```python
import re
from pathlib import Path
from typing import List
from app.models import BugReport


class BugReportService:
    """Bug 报告扫描与解析服务"""

    def list_bug_reports(self, project_path: str) -> List[BugReport]:
        """扫描被管理项目 docs/bug/ 目录，返回 Bug 报告摘要列表"""
        bug_dir = Path(project_path) / "docs/bug"
        if not bug_dir.exists():
            return []

        reports = []
        for md_file in bug_dir.glob("*.md"):
            report = self._parse_file(md_file)
            if report:
                reports.append(report)

        reports.sort(key=lambda r: r.createdAt, reverse=True)
        return reports

    def _parse_file(self, md_file: Path) -> BugReport | None:
        """解析单个 Bug 报告文件"""
        filename = md_file.name

        # 文件名至少需要：YYYY-MM-DD-x-x-x.md（16 个字符）
        if len(filename) < 16 or not filename.endswith(".md"):
            return None

        stem = filename[:-3]
        date_str = stem[:10]
        rest = stem[11:]

        parts = rest.split("-", 2)
        if len(parts) < 3:
            return None

        module, feature, description = parts[0], parts[1], parts[2]

        # 从文件内容提取 taskId
        task_id = ""
        try:
            content = md_file.read_text(encoding="utf-8")
            match = re.search(r"\*\*任务 ID\*\*：(.+)", content)
            if match:
                task_id = match.group(1).strip()
        except Exception:
            pass

        return BugReport(
            filename=filename,
            relativePath=f"docs/bug/{filename}",
            taskId=task_id,
            module=module,
            feature=feature,
            description=description,
            createdAt=date_str,
        )
```

**操作文件**：`backend/app/services/bug_report_service.py`（新建）

---

## T-03 创建 bug 路由

创建 `backend/app/routers/bug.py`，实现 Bug 报告列表接口。

```python
from fastapi import APIRouter
from typing import List
from app.services.bug_report_service import BugReportService
from app.services.project_service import ProjectService
from app.models import BugReport

router = APIRouter(prefix="/api/projects", tags=["bug"])

bug_report_service = BugReportService()
project_service = ProjectService()


@router.get("/{projectId}/bugs", response_model=List[BugReport])
async def list_bug_reports(projectId: str):
    """获取项目的 Bug 报告列表"""
    project = project_service.get_project(projectId)
    return bug_report_service.list_bug_reports(project.path)
```

**操作文件**：`backend/app/routers/bug.py`（新建）

---

## T-04 注册 bug 路由

在 `backend/app/main.py` 中导入并注册 bug 路由。

```python
from app.routers import project, task, process, execution, log, review, bug

# 在 app.include_router(review.router) 之后添加：
app.include_router(bug.router)
```

**操作文件**：`backend/app/main.py`（修改）

---

## T-05 验证 Bug 报告服务

```bash
cd backend
python -c "
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmpdir:
    bug_dir = Path(tmpdir, 'docs', 'bug')
    bug_dir.mkdir(parents=True)

    # 写入测试 Bug 报告文件
    (bug_dir / '2026-02-27-用户模块-登录功能-错误提示未显示.md').write_text(
        '# Bug 报告\n\n- **任务 ID**：test-task-uuid\n- **模块**：用户模块\n',
        encoding='utf-8'
    )

    import sys
    sys.path.insert(0, '.')
    from app.services.bug_report_service import BugReportService

    svc = BugReportService()

    # 测试 docs/bug/ 不存在时
    reports = svc.list_bug_reports('/nonexistent')
    assert reports == []
    print('空目录返回空列表: OK')

    # 测试正常扫描
    reports = svc.list_bug_reports(tmpdir)
    assert len(reports) == 1
    r = reports[0]
    assert r.module == '用户模块'
    assert r.feature == '登录功能'
    assert r.description == '错误提示未显示'
    assert r.taskId == 'test-task-uuid'
    assert r.createdAt == '2026-02-27'
    print(f'解析 Bug 报告: OK -> module={r.module}, taskId={r.taskId}')

print('所有验证通过')
"
```

**操作文件**：无（验证步骤）
