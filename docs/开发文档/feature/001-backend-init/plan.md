# 技术方案：后端工程初始化

> 任务编号：M1-T01

---

## 架构设计

### 1.1 FastAPI 应用架构

```
main.py (uvicorn 入口)
  └── app.main:create_app()
       ├── FastAPI() 实例
       ├── CORS 中间件配置
       └── 挂载 router (后续)
```

### 1.2 模块职责

| 文件/模块 | 职责 |
| ---------- | ---- |
| `backend/main.py` | uvicorn 启动入口，直接导入并运行 `app.main:app` |
| `backend/app/main.py` | FastAPI 应用工厂函数，配置 CORS 并返回 app 实例 |
| `backend/requirements.txt` | Python 依赖声明文件 |

---

## 数据结构

本任务不涉及持久化数据结构，仅涉及配置：

### 1.1 应用配置

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
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

### 1.2 启动入口

```python
# backend/main.py
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

---

## 接口定义

本任务暂无业务接口，仅提供根路径健康检查：

```
GET /

响应 200：{"message": "Claude Code Manager API"}
```

---

## 技术选型

| 技术点 | 选型 | 说明 |
| ------- | ---- | ---- |
| Web 框架 | FastAPI | 现代异步框架，自动生成 OpenAPI 文档 |
| ASGI 服务器 | uvicorn | 官方推荐，性能优秀 |
| CORS 中间件 | FastAPI 内置 CORSMiddleware | 简单可靠 |
