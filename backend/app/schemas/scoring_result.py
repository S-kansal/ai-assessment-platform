from datetime import datetime

from pydantic import BaseModel


class ScoringRead(BaseModel):
    id: str
    assessment_id: str
    raw_scores: dict[str, float]
    normalized_scores: dict[str, float]
    aggregate_score: float
    weighting_version: str
    created_at: datetime
