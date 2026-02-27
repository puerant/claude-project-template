# 功能需求：后端工程初始化

> 任务编号：M1-T01
> 模块：后端基础

---

## 用户故事

作为 Claude Code Manager 的开发者，我需要搭建 Python + FastAPI 后端工程骨架，以便后续在此基础上实现核心业务功能。

---

## 功能描述

建立标准的 FastAPI 工程结构，配置依赖管理、跨域支持和自动数据目录创建。

### 1.1 工程结构

按架构设计建立 `backend/app/` 目录：

```
backend/
├── app/
│   ├── routers/       # HTTP 路由
│   ├── services/      # 业务逻辑
│   ├── core/          # 核心能力
│   ├── models/        # Pydantic 数据模型
│   └── main.py        # FastAPI 应用入口
├── data/
│   ├── projects.json
│   ├── tasks/
│   └── logs/
├── requirements.txt
└── main.py             # uvicorn 启动入口
```

### 1.2 依赖管理

`requirements.txt` 包含以下依赖：

- `fastapi>=0.104.0` — Web 框架
- `uvicorn[standard]>=0.24.0` — ASGI 服务器
- `pydantic>=2.0.0` — 数据验证
- `python-multipart>=0.0.6` — 表单解析（后续添加项目时可能需要）
- `sse-starlette>=1.6.5` — SSE 支持

### 1.3 跨域配置

配置 CORS 允许前端 `http://localhost:5173` 跨域访问后端 API。

### 1.4 数据目录初始化

首次启动时自动创建 `data/` 及其子目录，避免后续文件操作因目录不存在而失败。

---

## 验收标准

- [ ] `backend/` 目录结构符合 1.1 定义
- [ ] `requirements.txt` 包含 1.2 列出的全部依赖
- [ ] 执行 `uvicorn main:app --host 0.0.0.0 --port 8765` 服务启动成功
- [ ] 访问 `http://localhost:8765/` 返回 200 状态码
- [ ] 前端从 `http://localhost:5173` 可调用后端 API（无跨域错误）
- [ ] 首次启动后 `data/projects.json`、`data/tasks/`、`data/logs/` 目录自动创建

---

## 边界情况

| 场景 | 预期行为 |
| ---- | -------- |
| 端口 8765 被占用 | uvicorn 启动失败，打印端口占用错误 |
| data 目录权限不足 | 启动时打印权限错误，不静默失败 |
| requirements.txt 依赖安装失败 | pip install 时明确提示失败包名及原因 |
