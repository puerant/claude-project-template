# 原子任务：后端工程初始化

> 任务编号：M1-T01

---

## T-01 创建目录结构

创建以下目录：

```bash
mkdir -p backend/app/routers
mkdir -p backend/app/services
mkdir -p backend/app/core
mkdir -p backend/app/models
mkdir -p backend/data/tasks
mkdir -p backend/data/logs
touch backend/data/projects.json
```

**操作文件**：新建 7 个目录，新建 1 个文件

---

## T-02 创建 requirements.txt

创建 `backend/requirements.txt` 文件，内容如下：

```text
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
python-multipart>=0.0.6
sse-starlette>=1.6.5
```

**操作文件**：`backend/requirements.txt`（新建）

---

## T-03 创建 FastAPI 应用入口

创建 `backend/app/main.py` 文件，实现应用工厂函数和 CORS 配置。

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    return app
```

**操作文件**：`backend/app/main.py`（新建）

---

## T-04 创建 uvicorn 启动入口

创建 `backend/main.py` 文件，实现 uvicorn 启动逻辑。

```python
import uvicorn
from app.main import create_app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8765,
        log_level="info"
    )
```

**操作文件**：`backend/main.py`（新建）

---

## T-05 添加根路径健康检查

在 `backend/app/main.py` 中添加根路径处理器：

```python
@app.get("/")
async def root():
    return {"message": "Claude Code Manager API"}
```

**操作文件**：`backend/app/main.py`（修改）

---

## T-06 验证启动

执行以下命令验证服务可正常启动：

```bash
cd backend
python -m pip install -r requirements.txt
python main.py
```

另开终端执行：

```bash
curl http://localhost:8765/
```

预期返回：`{"message":"Claude Code Manager API"}`

**操作文件**：无（验证步骤）
