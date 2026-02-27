from fastapi import HTTPException


class PathNotFoundError(HTTPException):
    """路径不存在错误 (40001)"""

    def __init__(self, detail: str = "路径不存在"):
        super().__init__(status_code=400, detail={"code": 40001, "message": detail})


class TaskListNotFoundError(HTTPException):
    """任务清单文件未找到错误 (40001)"""

    def __init__(self):
        super().__init__(
            status_code=400,
            detail={"code": 40001, "message": "未找到 docs/开发文档/任务清单.md"},
        )


class DuplicatePathError(HTTPException):
    """路径重复错误 (40901)"""

    def __init__(self):
        super().__init__(status_code=409, detail={"code": 40901, "message": "路径已存在"})


class ProjectNotFoundError(HTTPException):
    """项目不存在错误 (40401)"""

    def __init__(self):
        super().__init__(status_code=404, detail={"code": 40401, "message": "项目不存在"})
