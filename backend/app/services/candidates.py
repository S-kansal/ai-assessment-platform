from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.models.candidate import Candidate
from app.models.user import User


def create_candidate(
    db: Session,
    organization_id: str,
    name: str,
    email: str,
    password: str,
) -> Candidate:
    normalized_email = email.lower()
    existing_candidate = db.scalar(
        select(Candidate).where(
            Candidate.organization_id == organization_id,
            Candidate.email == normalized_email,
        )
    )
    if existing_candidate is not None:
        raise ConflictError("Candidate email already exists in this organization")

    existing_user = db.scalar(select(User).where(User.email == normalized_email))
    if existing_user is not None:
        raise ConflictError("Email is already registered")

    candidate = Candidate(
        organization_id=organization_id,
        name=name.strip(),
        email=normalized_email,
    )
    db.add(candidate)
    db.flush()

    candidate_user = User(
        organization_id=organization_id,
        candidate_id=candidate.id,
        email=normalized_email,
        password_hash=hash_password(password),
        role="candidate",
        is_active=True,
    )
    db.add(candidate_user)
    db.flush()
    return candidate


def list_candidates(db: Session, organization_id: str) -> list[Candidate]:
    return list(
        db.scalars(
            select(Candidate)
            .where(Candidate.organization_id == organization_id)
            .order_by(Candidate.created_at.desc())
        )
    )


def get_candidate(db: Session, organization_id: str, candidate_id: str) -> Candidate:
    candidate = db.scalar(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.organization_id == organization_id,
        )
    )
    if candidate is None:
        raise NotFoundError("Candidate not found")
    return candidate
