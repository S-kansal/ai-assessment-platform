from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import (
    AuthContext,
    envelope,
    get_current_user,
    get_db,
    require_candidate_self,
    require_roles,
)
from app.schemas.candidate import CandidateCreateRequest
from app.services.candidates import create_candidate, get_candidate, list_candidates


router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("")
def create_candidate_route(
    body: CandidateCreateRequest,
    user: AuthContext = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> dict:
    candidate = create_candidate(
        db,
        user.organization_id,
        body.name,
        body.email,
        body.password,
    )
    db.commit()
    return envelope(
        {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "created_at": candidate.created_at.isoformat(),
        }
    )


@router.get("")
def list_candidates_route(
    user: AuthContext = Depends(require_roles("admin", "reviewer")),
    db: Session = Depends(get_db),
) -> dict:
    candidates = list_candidates(db, user.organization_id)
    return envelope(
        [
            {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "created_at": candidate.created_at.isoformat(),
            }
            for candidate in candidates
        ]
    )


@router.get("/{candidate_id}")
def get_candidate_route(
    candidate_id: str,
    user: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    require_candidate_self(candidate_id, user)
    candidate = get_candidate(db, user.organization_id, candidate_id)
    return envelope(
        {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "created_at": candidate.created_at.isoformat(),
        }
    )
