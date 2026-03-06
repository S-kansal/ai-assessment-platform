"""Pilot API routes — registration, feedback, analytics, and assessment start."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session as DbSession
from sqlalchemy import func

from app.database import get_db
from app.models.candidate import Candidate
from app.models.session import Session
from app.models.telemetry import TelemetryEvent
from app.evaluation.models import EvaluationResult
from app.scoring.models import CandidateScore
from app.pilot.models import PilotParticipant, PilotFeedback, PilotResultsSummary
from app.org.models import Organization
from app.core.logging import get_logger

router = APIRouter(prefix="/pilot", tags=["pilot"])
logger = get_logger("pilot")

PILOT_ORG_SLUG = "pilot-lab"


# ── Schemas ────────────────────────────────────────

class PilotRegisterRequest(BaseModel):
    name: str
    email: str
    years_experience: Optional[int] = None
    primary_role: Optional[str] = None
    llm_experience_level: Optional[str] = None
    company: Optional[str] = None


class PilotFeedbackRequest(BaseModel):
    candidate_id: str
    task_realism: Optional[int] = None
    difficulty: Optional[int] = None
    evaluation_fairness: Optional[int] = None
    instruction_clarity: Optional[int] = None
    overall_experience: Optional[int] = None
    feedback_text: Optional[str] = None


# ── Helpers ────────────────────────────────────────

def _get_pilot_org(db: DbSession) -> Organization:
    """Get or create the pilot-lab organization."""
    org = db.query(Organization).filter(Organization.slug == PILOT_ORG_SLUG).first()
    if not org:
        org = Organization(name="Pilot Lab", slug=PILOT_ORG_SLUG)
        db.add(org)
        db.commit()
        db.refresh(org)
    return org


# ── Routes ─────────────────────────────────────────

@router.post("/register")
def pilot_register(body: PilotRegisterRequest, db: DbSession = Depends(get_db)):
    """Register a pilot participant — creates candidate + participant record."""
    org = _get_pilot_org(db)

    # Check duplicate
    existing = db.query(Candidate).filter(Candidate.email == body.email).first()
    if existing:
        # Return existing candidate for resumption
        logger.info("pilot_resume", email=body.email, candidate_id=existing.id)
        return {
            "candidate_id": existing.id,
            "message": "Welcome back! Resuming your assessment.",
            "is_returning": True,
        }

    # Create candidate
    candidate = Candidate(name=body.name, email=body.email, organization_id=org.id)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    # Create participant record
    participant = PilotParticipant(
        candidate_id=candidate.id,
        email=body.email,
        years_experience=body.years_experience,
        primary_role=body.primary_role,
        llm_experience_level=body.llm_experience_level,
        company=body.company,
    )
    db.add(participant)
    db.commit()

    logger.info("pilot_registered", candidate_id=candidate.id, email=body.email,
                role=body.primary_role, experience=body.years_experience)

    return {
        "candidate_id": candidate.id,
        "message": "Registration successful. Starting assessment...",
        "is_returning": False,
    }


@router.post("/feedback")
def pilot_feedback(body: PilotFeedbackRequest, db: DbSession = Depends(get_db)):
    """Submit pilot feedback survey."""
    candidate = db.query(Candidate).filter(Candidate.id == body.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    feedback = PilotFeedback(
        candidate_id=body.candidate_id,
        task_realism=body.task_realism,
        difficulty=body.difficulty,
        evaluation_fairness=body.evaluation_fairness,
        instruction_clarity=body.instruction_clarity,
        overall_experience=body.overall_experience,
        feedback_text=body.feedback_text,
    )
    db.add(feedback)
    db.commit()

    logger.info("pilot_feedback_submitted", candidate_id=body.candidate_id)
    return {"status": "feedback_received"}


@router.get("/analytics")
def pilot_analytics(db: DbSession = Depends(get_db)):
    """Pilot monitoring dashboard data."""
    org = _get_pilot_org(db)

    total_participants = db.query(PilotParticipant).count()
    total_candidates = db.query(Candidate).filter(
        Candidate.organization_id == org.id
    ).count()

    # Telemetry count
    telemetry_count = db.query(TelemetryEvent).filter(
        TelemetryEvent.organization_id == org.id
    ).count()

    # Scores
    scores = db.query(CandidateScore).filter(
        CandidateScore.candidate_id.in_(
            db.query(Candidate.id).filter(Candidate.organization_id == org.id)
        )
    ).all()

    avg_score = 0
    if scores:
        avg_score = round(sum(s.score for s in scores) / len(scores), 1)

    # Feedback summary
    feedback_count = db.query(PilotFeedback).count()
    feedback_rows = db.query(PilotFeedback).all()
    avg_feedback = {}
    if feedback_rows:
        for field in ["task_realism", "difficulty", "evaluation_fairness",
                       "instruction_clarity", "overall_experience"]:
            vals = [getattr(f, field) for f in feedback_rows if getattr(f, field)]
            avg_feedback[field] = round(sum(vals) / len(vals), 1) if vals else None

    return {
        "total_participants": total_participants,
        "total_candidates": total_candidates,
        "telemetry_events": telemetry_count,
        "avg_score": avg_score,
        "feedback_responses": feedback_count,
        "avg_feedback": avg_feedback,
    }
