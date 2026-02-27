import re
from typing import Optional


class OutputParser:
    """Claude Code 输出解析器"""

    PATTERN_SUCCESS = r"^SUCCESS$"
    PATTERN_FAILURE = r"^FAILURE:\s*(.+)$"

    def parse(self, output: str) -> tuple[bool, Optional[str]]:
        """
        解析输出，识别成功或失败标记

        Returns:
            (is_success, failure_reason): is_success=True 表示成功，False 表示失败；
            failure_reason 仅在失败时包含原因字符串
        """
        lines = output.strip().split("\n")

        # 从最后一行开始匹配
        for line in reversed(lines):
            line = line.strip()

            # 匹配 SUCCESS
            if re.match(self.PATTERN_SUCCESS, line, re.IGNORECASE):
                return (True, None)

            # 匹配 FAILURE: <原因>
            match = re.match(self.PATTERN_FAILURE, line, re.IGNORECASE)
            if match:
                return (False, match.group(1).strip())

        # 未找到结果标记
        return (None, None)

    def has_result(self, output: str) -> bool:
        """检查输出中是否包含结果标记"""
        result, _ = self.parse(output)
        return result is not None
