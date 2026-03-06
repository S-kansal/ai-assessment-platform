from typing import Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from app.database import get_db
from app.scoring.scoring_service import compute_candidate_scores

router = APIRouter(prefix="/scores", tags=["scoring"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ScoreComputeRequest(BaseModel):
    candidate_id: str


class TaskScoreItem(BaseModel):
    task_id: str
    task_run_id: str
    task_score: float


class ScoreComputeResponse(BaseModel):
    candidate_id: str
    capabilities: Dict[str, float]
    task_scores: List[TaskScoreItem]


# ---------------------------------------------------------------------------
# POST /scores/compute
# ---------------------------------------------------------------------------

@router.post("/compute", response_model=ScoreComputeResponse)
def compute_scores_endpoint(
    body: ScoreComputeRequest,
    db: DbSession = Depends(get_db),
):
    """Compute and return the capability profile for a candidate."""
    result = compute_candidate_scores(db, body.candidate_id)
    return ScoreComputeResponse(**result)
