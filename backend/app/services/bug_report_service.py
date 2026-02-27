import re
from pathlib import Path
from typing import List
from app.models import BugReport


class BugReportService:
    """Bug 报告扫描与解析服务"""

    def list_bug_reports(self, project_path: str) -> List[BugReport]:
        """扫描被管理项目 docs/bug/ 目录，返回 Bug 报告摘要列表（按 createdAt 降序）"""
        bug_dir = Path(project_path) / "docs/bug"
        if not bug_dir.exists():
            return []

        reports = []
        for md_file in bug_dir.glob("*.md"):
            report = self._parse_file(md_file)
            if report:
                reports.append(report)

        reports.sort(key=lambda r: r.createdAt, reverse=True)
        return reports

    def _parse_file(self, md_file: Path) -> BugReport | None:
        """解析单个 Bug 报告文件"""
        filename = md_file.name

        # 文件名至少需要：YYYY-MM-DD-x-x-x.md
        if len(filename) < 16 or not filename.endswith(".md"):
            return None

        stem = filename[:-3]      # 去掉 .md
        date_str = stem[:10]      # 前 10 位为日期 YYYY-MM-DD
        rest = stem[11:]          # 日期后剩余部分

        parts = rest.split("-", 2)
        if len(parts) < 3:
            return None

        module, feature, description = parts[0], parts[1], parts[2]

        # 从文件内容提取 taskId
        task_id = ""
        try:
            content = md_file.read_text(encoding="utf-8")
            match = re.search(r"\*\*任务 ID\*\*：(.+)", content)
            if match:
                task_id = match.group(1).strip()
        except Exception:
            pass

        return BugReport(
            filename=filename,
            relativePath=f"docs/bug/{filename}",
            taskId=task_id,
            module=module,
            feature=feature,
            description=description,
            createdAt=date_str,
        )
