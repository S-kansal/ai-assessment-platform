"""Database model for evaluation results."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON
from app.database import Base


class EvaluationResult(Base):
    """Stores structured evaluation scores for a completed task run."""

    __tablename__ = "evaluation_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(
        String(36), ForeignKey("organizations.id"), nullable=True,
    )
    task_run_id = Column(
        String(36),
        ForeignKey("task_runs.id"),
        nullable=False,
    )
    task_type = Column(String(64), nullable=True)

    # Scores (0–1)
    diagnostic_score = Column(Float, nullable=False, default=0.0)
    success_score = Column(Float, nullable=False, default=0.0)
    efficiency_score = Column(Float, nullable=False, default=0.0)
    iteration_score = Column(Float, nullable=False, default=0.0)

    # Raw metrics for auditability
    simulation_runs = Column(Integer, nullable=True)
    prompt_edits = Column(Integer, nullable=True)
    retrieval_inspections = Column(Integer, nullable=True)
    time_to_solution = Column(Float, nullable=True)

    # Debug trace
    evaluation_trace = Column(JSON, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

