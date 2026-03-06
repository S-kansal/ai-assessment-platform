import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, JSON
from app.database import Base


class Task(Base):
    """A task definition that can be assigned within an assessment session."""

    __tablename__ = "tasks"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    capability_target = Column(String(64), nullable=False)
    task_type = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    simulation_type = Column(String(64), nullable=False)
    failure_mode = Column(String(64), nullable=True)
    simulation_config = Column(JSON, nullable=True, default=dict)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

