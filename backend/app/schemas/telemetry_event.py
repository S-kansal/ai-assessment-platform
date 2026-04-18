from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TelemetryCreateRequest(BaseModel):
    task_run_id: str
    event_type: str = Field(min_length=3, max_length=64)
    monotonic_timestamp_ms: int = Field(ge=0)
    payload: dict[str, Any] = Field(default_factory=dict)


class TelemetryRead(BaseModel):
    id: str
    event_type: str
    monotonic_timestamp_ms: int
    payload: dict[str, Any]
    created_at: datetime
