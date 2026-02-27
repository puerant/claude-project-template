# 技术方案：Bug 报告列表接口

> 任务编号：M2-T10
> 模块：后端服务

---

## 架构设计

### 新增文件

| 文件 | 说明 |
| ---- | ---- |
| `backend/app/services/bug_report_service.py` | BugReportService：扫描 + 解析 Bug 报告 |
| `backend/app/routers/bug.py` | Bug API 路由 |

### 修改文件

| 文件 | 修改内容 |
| ---- | -------- |
| `backend/app/models/__init__.py` | 新增 `BugReport` Pydantic 模型 |
| `backend/app/main.py` | 注册 bug 路由 |

---

## BugReportService 设计

```python
class BugReportService:
    def list_bug_reports(project_path: str) -> List[BugReport]
```

**实现逻辑**：

1. 扫描 `<project_path>/docs/bug/*.md`
2. 对每个文件：
   - 从文件名解析 date / module / feature / description
   - 从文件内容提取 taskId（正则匹配 `\*\*任务 ID\*\*：(.+)`）
3. 按 `createdAt` 降序排列后返回

**文件名解析**（文件名示例：`2026-02-27-用户模块-登录功能-错误提示未显示.md`）：

```python
stem = filename[:-3]          # 去掉 .md
date = stem[:10]              # 前 10 位为日期
rest = stem[11:]              # 日期后剩余部分
parts = rest.split('-', 2)    # 最多分 3 份：module / feature / description
```

若 parts 长度不足，视为格式不符合规范，跳过。

---

## 路由设计

```
GET /api/projects/{projectId}/bugs
```

- 调用 `ProjectService.get_project(projectId)` 获取项目路径
- 调用 `BugReportService.list_bug_reports(project_path)` 返回列表
- 项目不存在时 `ProjectService.get_project` 已抛出 404

---

## 依赖关系

```
bug.py
  └─ ProjectService.get_project()
  └─ BugReportService.list_bug_reports()
```
