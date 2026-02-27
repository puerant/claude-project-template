from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
