"""Organization (tenant) database model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime
from app.database import Base


class Organization(Base):
    """A tenant (company) on the platform."""

    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
