# 技术方案：JSON 文件持久化层

> 任务编号：M1-T03

---

## 架构设计

### 1.1 模块位置

```
backend/app/core/
└── file_utils.py      # JSON 文件读写工具函数
```

### 1.2 函数签名

```python
from typing import TypeVar, Generic, Any
from pathlib import Path

T = TypeVar('T', bound=dict | list)

def read_json(path: str, default: T | None = None) -> T:
    """读取 JSON 文件并解析为 Python 对象/列表"""

def write_json(path: str, data: dict | list) -> None:
    """原子写入 JSON 文件"""
```

---

## 数据结构

本任务不涉及持久化数据结构，仅定义工具函数的输入输出。

### 2.1 read_json 返回值约定

- `projects.json`：默认返回 `[]`（空列表）
- `tasks/{id}.json`：默认返回 `[]`（空列表）
- 其他场景：由调用方指定默认值

### 2.2 write_json 路径约定

- 列表场景：文件扩展名 `.json`，内容为 JSON 数组
- 对象场景：文件扩展名 `.json`，内容为 JSON 对象

---

## 接口定义

本任务不涉及 HTTP 接口，仅提供内部工具函数。

---

## 技术选型

| 技术点 | 选型 | 说明 |
| ------- | ---- | ---- |
| JSON 解析 | Python 内置 `json` 模块 | 零依赖、标准库 |
| 原子写入 | 临时文件 + `os.rename()` | 原子操作保证数据完整性 |
| 文件锁 | `fcntl.flock()` (Unix) / `msvcrt.locking()` (Windows) | 跨平台并发保护 |
| 路径处理 | `pathlib.Path` | 现代化路径操作 |
| 目录创建 | `Path.parent.mkdir(parents=True, exist_ok=True)` | 自动创建父目录 |
