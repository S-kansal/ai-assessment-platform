"""Authentication service — registration, login, password hashing."""

import re
from passlib.context import CryptContext
from sqlalchemy.orm import Session as DbSession
from fastapi import HTTPException

from app.org.models import Organization
from app.auth.models import User, AuditLog
from app.auth.jwt_service import create_access_token
from app.core.logging import get_logger

logger = get_logger("auth")

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def _verify_password(password: str, stored_hash: str) -> bool:
    return _pwd_context.verify(password, stored_hash)


def _slugify(name: str) -> str:
    """Convert company name to URL-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug


def register_organization(db: DbSession, company_name: str,
                          admin_email: str, password: str) -> dict:
    """Create a new organization and its admin user."""
    slug = _slugify(company_name)

    # Check for duplicate slug
    existing = db.query(Organization).filter(Organization.slug == slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="Organization already exists")

    # Check for duplicate email
    existing_user = db.query(User).filter(User.email == admin_email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    org = Organization(name=company_name, slug=slug)
    db.add(org)
    db.flush()

    user = User(
        email=admin_email,
        password_hash=_hash_password(password),
        organization_id=org.id,
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(org)
    db.refresh(user)

    # Audit
    db.add(AuditLog(
        user_id=user.id,
        organization_id=org.id,
        action="org_registered",
        detail=f"Organization '{company_name}' created",
    ))
    db.commit()

    logger.info("org_registered", org_id=org.id, slug=org.slug, admin_email=admin_email)

    return {
        "organization_id": org.id,
        "organization_slug": org.slug,
        "admin_user_id": user.id,
    }


def login_user(db: DbSession, email: str, password: str) -> dict:
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not _verify_password(password, user.password_hash):
        logger.warning("login_failed", email=email)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({
        "user_id": user.id,
        "organization_id": user.organization_id,
        "role": user.role,
        "email": user.email,
    })

    # Audit
    db.add(AuditLog(
        user_id=user.id,
        organization_id=user.organization_id,
        action="user_login",
    ))
    db.commit()

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "organization_id": user.organization_id,
        "role": user.role,
    }
