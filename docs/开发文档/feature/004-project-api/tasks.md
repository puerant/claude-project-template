# 原子任务：项目管理模块与 API

> 任务编号：M2-T01

---

## T-01 创建 services 目录和 service 基类

创建 `backend/app/services/` 目录及其 `__init__.py` 文件。

创建 `backend/app/services/project_service.py`，定义 `ProjectService` 类。

```python
from pathlib import Path
from typing import List
from app.core import read_json, write_json
from app.models import Project, TaskStats

class ProjectService:
    """项目管理服务"""

    def __init__(self, data_dir: str = "data"):
        self.projects_file = Path(data_dir) / "projects.json"

    def list_projects(self) -> List[Project]:
        """获取所有项目列表"""
        projects = read_json(str(self.projects_file), default=[])
        return [Project(**p) for p in projects]

    def save_projects(self, projects: List[Project]) -> None:
        """保存项目列表"""
        projects_data = [p.model_dump() for p in projects]
        write_json(str(self.projects_file), projects_data)
```

**操作文件**：新建 1 个目录、2 个文件

---

## T-02 实现项目添加服务方法

在 `ProjectService` 中添加 `add_project` 方法，包含路径校验和重复性检查。

```python
    def add_project(self, name: str, path: str) -> Project:
        """添加新项目"""
        project_path = Path(path)

        # 校验路径存在
        if not project_path.exists():
            raise ValueError("路径不存在")

        # 校验包含任务清单文件
        task_list_file = project_path / "docs/开发文档/任务清单.md"
        if not task_list_file.exists():
            raise ValueError("未找到 docs/开发文档/任务清单.md")

        # 校验路径未重复
        projects = self.list_projects()
        for p in projects:
            if p.path == path:
                raise ValueError("路径已存在")

        # 创建新项目
        new_project = Project(name=name, path=path, taskStats=TaskStats())
        projects.append(new_project)
        self.save_projects(projects)

        return new_project
```

**操作文件**：`backend/app/services/project_service.py`（修改）

---

## T-03 实现项目删除服务方法

在 `ProjectService` 中添加 `delete_project` 方法。

```python
    def delete_project(self, project_id: str) -> None:
        """删除项目（仅移除记录，不删本地文件）"""
        projects = self.list_projects()
        projects = [p for p in projects if p.id != project_id]

        if len(projects) == len(self.list_projects()):
            raise ValueError("项目不存在")

        self.save_projects(projects)
```

**操作文件**：`backend/app/services/project_service.py`（修改）

---

## T-04 创建异常类

创建 `backend/app/core/exceptions.py`，定义自定义异常类。

```python
from fastapi import HTTPException

class PathNotFoundError(HTTPException):
    """路径不存在错误 (40001)"""
    def __init__(self, detail: str = "路径不存在"):
        super().__init__(status_code=400, detail={"code": 40001, "message": detail})

class TaskListNotFoundError(HTTPException):
    """任务清单文件未找到错误 (40001)"""
    def __init__(self):
        super().__init__(status_code=400, detail={"code": 40001, "message": "未找到 docs/开发文档/任务清单.md"})

class DuplicatePathError(HTTPException):
    """路径重复错误 (40901)"""
    def __init__(self):
        super().__init__(status_code=409, detail={"code": 40901, "message": "路径已存在"})

class ProjectNotFoundError(HTTPException):
    """项目不存在错误 (40401)"""
    def __init__(self):
        super().__init__(status_code=404, detail={"code": 40401, "message": "项目不存在"})
```

**操作文件**：`backend/app/core/exceptions.py`（新建）

---

## T-05 更新 service 使用自定义异常

修改 `ProjectService` 中的 `add_project` 和 `delete_project` 方法，使用自定义异常。

```python
from app.core.exceptions import PathNotFoundError, TaskListNotFoundError, DuplicatePathError

    def add_project(self, name: str, path: str) -> Project:
        """添加新项目"""
        project_path = Path(path)

        if not project_path.exists():
            raise PathNotFoundError()

        task_list_file = project_path / "docs/开发文档/任务清单.md"
        if not task_list_file.exists():
            raise TaskListNotFoundError()

        projects = self.list_projects()
        for p in projects:
            if p.path == path:
                raise DuplicatePathError()

        new_project = Project(name=name, path=path, taskStats=TaskStats())
        projects.append(new_project)
        self.save_projects(projects)

        return new_project
```

```python
from app.core.exceptions import ProjectNotFoundError

    def delete_project(self, project_id: str) -> None:
        """删除项目"""
        projects = self.list_projects()
        original_count = len(projects)
        projects = [p for p in projects if p.id != project_id]

        if len(projects) == original_count:
            raise ProjectNotFoundError()

        self.save_projects(projects)
```

**操作文件**：`backend/app/services/project_service.py`（修改）

---

## T-06 创建路由文件

创建 `backend/app/routers/project.py`，实现项目 API 路由。

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.project_service import ProjectService
from app.models import Project

router = APIRouter(prefix="/api/projects", tags=["项目"])

project_service = ProjectService()

class CreateProjectRequest(BaseModel):
    """创建项目请求"""
    name: str
    path: str

@router.get("", response_model=List[Project])
async def list_projects():
    """获取项目列表"""
    return project_service.list_projects()

@router.post("", response_model=Project)
async def create_project(req: CreateProjectRequest):
    """创建项目"""
    return project_service.add_project(req.name, req.path)

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """删除项目"""
    project_service.delete_project(project_id)
    return {"message": "项目已删除"}
```

**操作文件**：`backend/app/routers/project.py`（新建）

---

## T-07 注册路由

在 `backend/app/main.py` 中注册项目路由。

```python
from app.routers import project

def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例"""
    app = FastAPI(
        title="Claude Code Manager",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(project.router)

    @app.get("/")
    async def root():
        return {"message": "Claude Code Manager API"}

    return app
```

**操作文件**：`backend/app/main.py`（修改）

---

## T-08 验证 API

启动服务并测试 API。

```bash
cd backend
python main.py
```

另开终端测试：

```bash
# 获取项目列表
curl http://localhost:8765/api/projects

# 创建项目
curl -X POST http://localhost:8765/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "测试项目", "path": "/tmp/test-project"}"

# 删除项目
curl -X DELETE http://localhost:8765/api/projects/{project-id}
```

**操作文件**：无（验证步骤）
