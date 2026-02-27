# 原子任务：JSON 文件持久化层

> 任务编号：M1-T03

---

## T-01 创建 core 目录

创建 `backend/app/core/` 目录。

```bash
mkdir -p backend/app/core
touch backend/app/core/__init__.py
```

**操作文件**：新建 1 个目录、1 个文件

---

## T-02 定义跨平台文件锁类

在 `backend/app/core/file_utils.py` 中创建 `FileLock` 上下文管理器，实现跨平台文件锁。

```python
import os
import fcntl
from contextlib import contextmanager
from typing import Optional

class FileLock:
    """跨平台文件锁上下文管理器"""

    def __init__(self, lock_file: str):
        self.lock_file = lock_file
        self.fp: Optional[object] = None

    def __enter__(self):
        """获取文件锁"""
        self.fp = open(self.lock_file, 'w')
        # Unix/Linux/macOS
        if os.name != 'nt':
            fcntl.flock(self.fp, fcntl.LOCK_EX)
        # Windows
        else:
            import msvcrt
            msvcrt.locking(self.fp.fileno(), msvcrt.LK_LOCK)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """释放文件锁"""
        if os.name != 'nt':
            fcntl.flock(self.fp, fcntl.LOCK_UN)
        else:
            import msvcrt
            msvcrt.locking(self.fp.fileno(), msvcrt.LK_UNLCK)
        self.fp.close()
        # 清理锁文件
        try:
            os.remove(self.lock_file)
        except OSError:
            pass
```

**操作文件**：`backend/app/core/file_utils.py`（新建）

---

## T-03 实现 read_json 函数

在 `backend/app/core/file_utils.py` 中添加 `read_json` 函数。

```python
from pathlib import Path
import json
from typing import TypeVar, Union

T = TypeVar('T', bound=Union[dict, list])

def read_json(path: str, default: Union[dict, list] | None = None) -> Union[dict, list]:
    """读取 JSON 文件，文件不存在时返回默认值"""
    file_path = Path(path)
    if not file_path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(f"File not found: {path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
```

**操作文件**：`backend/app/core/file_utils.py`（修改）

---

## T-04 实现 write_json 函数

在 `backend/app/core/file_utils.py` 中添加 `write_json` 函数，实现原子写入和并发保护。

```python
import tempfile
import shutil
from pathlib import Path

def write_json(path: str, data: dict | list) -> None:
    """原子写入 JSON 文件，使用文件锁保护并发写入"""
    file_path = Path(path)
    lock_path = Path(str(file_path) + ".lock")

    # 确保父目录存在
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with FileLock(str(lock_path)):
        # 写入临时文件
        temp_path = file_path.with_suffix('.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 原子重命名
        shutil.move(str(temp_path), str(file_path))
```

**操作文件**：`backend/app/core/file_utils.py`（修改）

---

## T-05 统一导出工具函数

在 `backend/app/core/__init__.py` 中导出工具函数。

```python
from .file_utils import read_json, write_json

__all__ = ["read_json", "write_json"]
```

**操作文件**：`backend/app/core/__init__.py`（新建）

---

## T-06 验证工具函数

创建测试脚本验证工具函数正确性。

```bash
# backend/tests/test_file_utils.py（可选）
python -c "
from app.core import read_json, write_json
import tempfile
import os

# 测试读写
temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
write_json(temp_file.name, {'test': 'data'})
result = read_json(temp_file.name)
print('Read result:', result)
assert result == {'test': 'data'}, '读写不一致'

os.unlink(temp_file.name)
print('验证通过')
"
```

**操作文件**：新建测试脚本（可选）
