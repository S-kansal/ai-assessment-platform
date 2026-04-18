from sqlalchemy.orm import Session

from app.scoring.engine import compute_scoring_result


def compute_scores(db: Session, organization_id: str, assessment_id: str):
    return compute_scoring_result(db, assessment_id, organization_id)
