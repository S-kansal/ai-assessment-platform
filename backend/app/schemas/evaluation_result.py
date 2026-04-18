from datetime import datetime

from pydantic import BaseModel


class EvaluationRead(BaseModel):
    id: str
    task_run_id: str
    dimension_scores: dict[str, float]
    formulas: dict
    evidence: dict
    total_score: float
    created_at: datetime
