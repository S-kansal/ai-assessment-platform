"""Pilot-specific data models for external testing."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from app.database import Base


class PilotParticipant(Base):
    """Background info about pilot testers."""

    __tablename__ = "pilot_participants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False)
    email = Column(String(255), nullable=False)
    years_experience = Column(Integer, nullable=True)
    primary_role = Column(String(100), nullable=True)
    llm_experience_level = Column(String(50), nullable=True)  # beginner/intermediate/advanced
    company = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PilotFeedback(Base):
    """Survey responses after assessment completion."""

    __tablename__ = "pilot_feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False)
    task_realism = Column(Integer, nullable=True)       # 1-5
    difficulty = Column(Integer, nullable=True)          # 1-5
    evaluation_fairness = Column(Integer, nullable=True) # 1-5
    instruction_clarity = Column(Integer, nullable=True) # 1-5
    overall_experience = Column(Integer, nullable=True)  # 1-5
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PilotResultsSummary(Base):
    """Simplified pilot analytics per candidate."""

    __tablename__ = "pilot_results_summary"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False)
    assessment_id = Column(String(36), nullable=True)
    final_score = Column(Float, nullable=True)
    rag_debug_score = Column(Float, nullable=True)
    prompt_engineering_score = Column(Float, nullable=True)
    simulation_runs = Column(Integer, nullable=True)
    prompt_edits = Column(Integer, nullable=True)
    completion_time = Column(Integer, nullable=True)  # seconds
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
