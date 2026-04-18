import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.security import hash_password
from app.models.organization import Organization
from app.models.user import User


def register_organization(
    db: Session,
    organization_name: str,
    organization_slug: str,
    admin_email: str,
    admin_password: str,
) -> Organization:
    normalized_slug = re.sub(r"[^a-z0-9-]+", "-", organization_slug.strip().lower()).strip("-")
    if not normalized_slug:
        raise ValidationError("Organization slug is invalid")

    existing_org = db.scalar(select(Organization).where(Organization.slug == normalized_slug))
    if existing_org is not None:
        raise ConflictError("Organization slug already exists")
    existing_user = db.scalar(select(User).where(User.email == admin_email.lower()))
    if existing_user is not None:
        raise ConflictError("Admin email is already registered")

    organization = Organization(name=organization_name.strip(), slug=normalized_slug)
    db.add(organization)
    db.flush()

    admin_user = User(
        organization_id=organization.id,
        email=admin_email.lower(),
        password_hash=hash_password(admin_password),
        role="admin",
        is_active=True,
    )
    db.add(admin_user)
    db.flush()
    return organization


def get_organization(db: Session, organization_id: str) -> Organization:
    organization = db.scalar(
        select(Organization).where(Organization.id == organization_id)
    )
    if organization is None:
        raise NotFoundError("Organization not found")
    return organization
