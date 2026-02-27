# 功能需求：Pydantic 数据模型定义

> 任务编号：M1-T02
> 模块：后端基础

---

## 用户故事

作为 Claude Code Manager 后端开发者，我需要定义系统全部 Pydantic 数据模型，以便建立后端的数据契约基础，确保接口参数和响应的类型安全。

---

## 功能描述

定义项目、任务、日志三大实体的 Pydantic 模型，以及任务类型和状态的枚举类型。

### 2.1 项目模型（Project）

包含以下字段：

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| id | str | 项目唯一标识（UUID） |
| name | str | 项目显示名称 |
| path | str | 项目本地绝对路径 |
| createdAt | str | 创建时间（ISO 8601） |
| taskStats | TaskStats | 任务统计（可选，列表接口返回时填充） |

#### TaskStats

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| total | int | 总任务数 |
| pending | int | 待开发数 |
| in_progress | int | 开发中数 |
| pending_review | int | 待 review 数 |
| completed | int | 已完成数 |
| failed | int | 失败数 |
| cancelled | int | 已取消数 |

### 2.2 任务模型（Task）

包含以下字段：

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| id | str | 任务唯一标识（UUID） |
| projectId | str | 所属项目 ID |
| type | TaskType | 任务类型：feature / bug |
| title | str | 任务标题 |
| description | str | 任务完整描述（Markdown 原文） |
| module | str | 所属模块 |
| status | TaskStatus | 任务状态 |
| acceptanceCriteria | list[str] | 验收标准列表 |
| branch | str \| None | 关联 Git 分支名 |
| worktreePath | str \| None | 关联 worktree 路径 |
| bugReportPath | str \| None | 关联 Bug 报告路径 |
| createdAt | str | 创建时间（ISO 8601） |
| updatedAt | str | 更新时间（ISO 8601） |

### 2.3 日志模型（LogEntry）

包含以下字段：

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| ts | str | 时间戳（ISO 8601） |
| stream | LogStream | 输出流类型：stdout / stderr |
| line | str | 日志行内容 |

### 2.4 枚举类型

#### TaskType

```python
class TaskType(str, Enum):
    FEATURE = "feature"
    BUG = "bug"
```

#### TaskStatus

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

#### LogStream

```python
class LogStream(str, Enum):
    STDOUT = "stdout"
    STDERR = "stderr"
```

---

## 验收标准

- [ ] `models/project.py` 定义 `Project` 和 `TaskStats` 模型
- [ ] `models/task.py` 定义 `Task` 模型以及 `TaskType`、`TaskStatus` 枚举
- [ ] `models/log.py` 定义 `LogEntry` 模型以及 `LogStream` 枚举
- [ ] 所有模型可正常通过 `model.model_dump()` 序列化为 JSON
- [ ] 所有模型可正常通过 `model.model_validate_json()` 从 JSON 反序列化
- [ ] 所有枚举类型的值与 PRD 定义完全一致

---

## 边界情况

| 场景 | 预期行为 |
| ---- | -------- |
| 字段类型不匹配 | Pydantic 在反序列化时抛出 `ValidationError` |
| 缺少必填字段 | Pydantic 反序列化时抛出 `ValidationError` |
| 可选字段为 null | 字段值应为 None，不抛异常 |
