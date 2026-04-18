from datetime import datetime

from pydantic import BaseModel


class TaskRead(BaseModel):
    id: str
    title: str
    task_type: str
    failure_modes: list[str]
    expected_diagnostic_path: list[str]


class TaskRunRead(BaseModel):
    id: str
    assessment_id: str
    task_id: str
    sequence_index: int
    status: str
    final_prompt: str | None = None
    final_query: str | None = None
    submitted_root_cause: str | None = None
    submitted_fix_summary: str | None = None
    started_at: datetime
    completed_at: datetime | None = None


class TaskSubmissionRequest(BaseModel):
    final_prompt: str
    final_query: str
    submitted_root_cause: str
    submitted_fix_summary: str
