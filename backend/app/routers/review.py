from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.services.task_service import TaskService
from app.services.file_write_service import FileWriteService
from app.services.project_service import ProjectService
from app.services.git_service import GitService
from app.models import TaskStatus, TaskType, Task
from app.core.exceptions import InvalidStatusTransitionError

router = APIRouter(prefix="/api/tasks", tags=["review"])

task_service = TaskService()
file_write_service = FileWriteService()
project_service = ProjectService()
git_service = GitService()


class ReviewRequest(BaseModel):
    result: str
    failedCriteria: List[str] = []


@router.post("/{taskId}/review")
async def review_task(taskId: str, body: ReviewRequest):
    """提交 Review 结果（pass → completed，fail → bug 报告 + 新 bug 任务）"""
    task, project_id = task_service.get_task_by_id(taskId)

    if task.status != TaskStatus.PENDING_REVIEW:
        raise InvalidStatusTransitionError()

    project = project_service.get_project(project_id)
    project_path = project.path

    tasks = task_service.list_tasks(project_id)

    if body.result == "pass":
        if task.worktreePath and task.branch:
            try:
                git_service.commit_and_push(task.worktreePath, f"feat: {task.title}")
            except Exception:
                pass
            try:
                git_service.remove_worktree(project_path, task.worktreePath)
            except Exception:
                pass

        task.status = TaskStatus.COMPLETED
        task.worktreePath = None
        task.updatedAt = datetime.now().isoformat()

        for i, t in enumerate(tasks):
            if t.id == taskId:
                tasks[i] = task
                break
        task_service.save_tasks(project_id, tasks)

        return {"status": "completed", "branch": task.branch}

    elif body.result == "fail":
        if not body.failedCriteria:
            raise HTTPException(
                status_code=400,
                detail={"code": 40001, "message": "failedCriteria 不能为空"},
            )

        bug_report_path = file_write_service.create_bug_report(
            project_path, task, body.failedCriteria
        )

        new_bug_task = Task(
            projectId=project_id,
            type=TaskType.BUG,
            title=f"修复: {task.title}",
            description=(
                f"关联 Bug 报告：{bug_report_path}\n\n"
                + "失败原因：\n"
                + "\n".join(f"- {c}" for c in body.failedCriteria)
            ),
            module=task.module,
            acceptanceCriteria=body.failedCriteria,
            bugReportPath=bug_report_path,
        )

        task.status = TaskStatus.FAILED
        task.bugReportPath = bug_report_path
        task.updatedAt = datetime.now().isoformat()

        for i, t in enumerate(tasks):
            if t.id == taskId:
                tasks[i] = task
                break
        tasks.append(new_bug_task)
        task_service.save_tasks(project_id, tasks)

        return {
            "status": "failed",
            "bugReportPath": bug_report_path,
            "newBugTaskId": new_bug_task.id,
        }

    else:
        raise HTTPException(
            status_code=400,
            detail={"code": 40001, "message": "result 必须为 pass 或 fail"},
        )
