from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session as DbSession

from app.database import get_db
from app.models.candidate import Candidate
from app.models.session import Session

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class CandidateCreateRequest(BaseModel):
    name: str
    email: str
    organization_id: str = None


class CandidateCreateResponse(BaseModel):
    candidate_id: str


class SessionCreateRequest(BaseModel):
    candidate_id: str


class SessionCreateResponse(BaseModel):
    session_id: str


# ---------------------------------------------------------------------------
# POST /candidates
# ---------------------------------------------------------------------------

@router.post("/candidates", response_model=CandidateCreateResponse)
def create_candidate(
    body: CandidateCreateRequest,
    db: DbSession = Depends(get_db),
):
    """Register a new candidate."""
    # Check for duplicate email
    existing = db.query(Candidate).filter(Candidate.email == body.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    candidate = Candidate(
        name=body.name,
        email=body.email,
        organization_id=body.organization_id,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return CandidateCreateResponse(candidate_id=candidate.id)


# ---------------------------------------------------------------------------
# POST /sessions
# ---------------------------------------------------------------------------

@router.post("/sessions", response_model=SessionCreateResponse)
def create_session(
    body: SessionCreateRequest,
    db: DbSession = Depends(get_db),
):
    """Start a new assessment session for a candidate."""
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == body.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    session = Session(candidate_id=body.candidate_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return SessionCreateResponse(session_id=session.id)
