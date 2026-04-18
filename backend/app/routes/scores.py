from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import envelope, get_db, require_roles
from app.models.scoring_result import ScoringResult
from app.services.scores import compute_scores


router = APIRouter(prefix="/scores", tags=["scores"])


@router.post("/{assessment_id}/compute")
def compute_scores_route(
    assessment_id: str,
    user=Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> dict:
    result = compute_scores(db, user.organization_id, assessment_id)
    db.commit()
    return envelope(
        {
            "id": result.id,
            "assessment_id": result.assessment_id,
            "raw_scores": result.raw_scores,
            "normalized_scores": result.normalized_scores,
            "aggregate_score": result.aggregate_score,
            "weighting_version": result.weighting_version,
            "created_at": result.created_at.isoformat(),
        }
    )


@router.get("/{assessment_id}")
def get_scores_route(
    assessment_id: str,
    user=Depends(require_roles("admin", "reviewer")),
    db: Session = Depends(get_db),
) -> dict:
    result = db.scalar(
        select(ScoringResult).where(
            ScoringResult.assessment_id == assessment_id,
            ScoringResult.organization_id == user.organization_id,
        )
    )
    return envelope(
        None
        if result is None
        else {
            "id": result.id,
            "assessment_id": result.assessment_id,
            "raw_scores": result.raw_scores,
            "normalized_scores": result.normalized_scores,
            "aggregate_score": result.aggregate_score,
            "weighting_version": result.weighting_version,
            "created_at": result.created_at.isoformat(),
        }
    )
