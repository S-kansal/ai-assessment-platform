from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError, ValidationError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.organization import Organization
from app.models.user import User


def login_user(db: Session, email: str, password: str) -> dict:
    user = db.scalar(select(User).where(User.email == email.lower(), User.is_active.is_(True)))
    if user is None or not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid email or password")

    token = create_access_token(
        {
            "sub": user.id,
            "organization_id": user.organization_id,
            "role": user.role,
            "candidate_id": user.candidate_id,
        }
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "organization_id": user.organization_id,
        "role": user.role,
        "candidate_id": user.candidate_id,
    }


def register_user(
    db: Session,
    organization_id: str,
    email: str,
    password: str,
    role: str,
    candidate_id: str | None = None,
) -> User:
    if role not in {"admin", "reviewer", "candidate"}:
        raise ValidationError("Unsupported role")

    organization = db.scalar(
        select(Organization).where(Organization.id == organization_id)
    )
    if organization is None:
        raise NotFoundError("Organization not found")

    normalized_email = email.lower()
    existing_user = db.scalar(select(User).where(User.email == normalized_email))
    if existing_user is not None:
        raise ConflictError("Email is already registered")

    user = User(
        organization_id=organization_id,
        candidate_id=candidate_id,
        email=normalized_email,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user
