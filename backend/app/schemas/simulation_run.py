from datetime import datetime

from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    task_run_id: str
    prompt_text: str = Field(min_length=1)
    query_text: str = Field(min_length=1)


class SimulationRead(BaseModel):
    id: str
    task_run_id: str
    prompt_text: str
    query_text: str
    retrieved_chunks: list[dict]
    debug_logs: list[str]
    response_text: str
    output_quality: dict
    confidence_score: float
    created_at: datetime
