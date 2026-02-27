from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import project, task, process, execution, log, review, bug

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
    app.include_router(task.router)
    app.include_router(process.router)
    app.include_router(execution.router)
    app.include_router(log.router)
    app.include_router(review.router)
    app.include_router(bug.router)

    @app.get("/")
    async def root():
        return {"message": "Claude Code Manager API"}

    return app
