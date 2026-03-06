import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey
from app.database import Base


class Session(Base):
    """An assessment session for a candidate."""

    __tablename__ = "sessions"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    organization_id = Column(
        String(36), ForeignKey("organizations.id"), nullable=True,
    )
    candidate_id = Column(
        String(36),
        ForeignKey("candidates.id"),
        nullable=False,
    )
    started_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status = Column(
        String(32),
        default="active",
        nullable=False,
    )

