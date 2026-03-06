"""User and audit log database models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey
from app.database import Base


class User(Base):
    """A platform user (recruiter, admin, viewer) belonging to an organization."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    organization_id = Column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    role = Column(String(32), nullable=False, default="viewer")  # admin | recruiter | viewer
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class AuditLog(Base):
    """Tracks user actions for compliance and security."""

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    action = Column(String(100), nullable=False)
    detail = Column(String(500), nullable=True)
    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
