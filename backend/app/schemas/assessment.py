from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.task import TaskRunRead


class AssessmentCreateRequest(BaseModel):
    candidate_id: str
    title: str = Field(default="AI Engineering Assessment", max_length=255)
    order_mode: str = Field(default="fixed")
    browser_session_id: str = Field(min_length=6, max_length=64)


class AssessmentRead(BaseModel):
    id: str
    candidate_id: str
    title: str
    status: str
    order_mode: str
    task_ids: list[str]
    current_task_index: int
    assigned_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    expires_at: datetime | None = None


class AssessmentProgressResponse(BaseModel):
    assessment: AssessmentRead
    active_task_run: TaskRunRead | None = None


class AssessmentSubmitRequest(BaseModel):
    task_run_id: str
    final_prompt: str
    final_query: str
    submitted_root_cause: str
    submitted_fix_summary: str
