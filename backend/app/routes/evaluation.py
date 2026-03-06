from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from app.database import get_db
from app.evaluation.evaluation_service import run_evaluation

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class EvaluationRequest(BaseModel):
    task_run_id: str


class EvaluationResponse(BaseModel):
    task_run_id: str
    diagnostic_score: float
    success_score: float
    efficiency_score: float
    iteration_score: float
    debug_log: List[str]


# ---------------------------------------------------------------------------
# POST /evaluation/run
# ---------------------------------------------------------------------------

@router.post("/run", response_model=EvaluationResponse)
def evaluate_endpoint(
    body: EvaluationRequest,
    db: DbSession = Depends(get_db),
):
    """Trigger evaluation for a completed task run."""
    result = run_evaluation(db, body.task_run_id)
    return EvaluationResponse(**result)
