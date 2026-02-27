import os
from contextlib import contextmanager
from typing import Optional, Union
from pathlib import Path
import json
import tempfile
import shutil


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
            import fcntl
            fcntl.flock(self.fp, fcntl.LOCK_EX)
        # Windows: 锁与文件句柄绑定，关闭文件即自动释放锁
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """释放文件锁"""
        if os.name != 'nt':
            import fcntl
            fcntl.flock(self.fp, fcntl.LOCK_UN)
        self.fp.close()
        # 清理锁文件
        try:
            os.remove(self.lock_file)
        except OSError:
            pass


def read_json(path: str, default: Union[dict, list] | None = None) -> Union[dict, list]:
    """读取 JSON 文件，文件不存在时返回默认值"""
    file_path = Path(path)
    if not file_path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(f"File not found: {path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if not content.strip():
            # 空文件返回默认值
            if default is not None:
                return default
            return []
        return json.loads(content)


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


def read_json_lines(path: str) -> list:
    """读取 JSONL 文件，每行一个 JSON 对象"""
    file_path = Path(path)
    if not file_path.exists():
        return []

    lines = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(json.loads(line))
    return lines
