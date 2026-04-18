from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import envelope, get_db, rate_limit_dependency, require_roles
from app.services.evaluations import get_evaluation, run_evaluation


router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post(
    "/{task_run_id}/run",
    dependencies=[Depends(rate_limit_dependency("evaluations", settings.evaluation_rate_limit_per_minute))],
)
def run_evaluation_route(
    task_run_id: str,
    _user=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> dict:
    evaluation = run_evaluation(db, _user.organization_id, task_run_id)
    db.commit()
    return envelope(
        {
            "id": evaluation.id,
            "task_run_id": evaluation.task_run_id,
            "dimension_scores": evaluation.dimension_scores,
            "formulas": evaluation.formulas,
            "evidence": evaluation.evidence,
            "total_score": evaluation.total_score,
            "created_at": evaluation.created_at.isoformat(),
        }
    )


@router.get("/{task_run_id}")
def get_evaluation_route(
    task_run_id: str,
    _user=Depends(require_roles("admin", "reviewer")),
    db: Session = Depends(get_db),
) -> dict:
    evaluation = get_evaluation(db, _user.organization_id, task_run_id)
    return envelope(
        {
            "id": evaluation.id,
            "task_run_id": evaluation.task_run_id,
            "dimension_scores": evaluation.dimension_scores,
            "formulas": evaluation.formulas,
            "evidence": evaluation.evidence,
            "total_score": evaluation.total_score,
            "created_at": evaluation.created_at.isoformat(),
        }
    )
