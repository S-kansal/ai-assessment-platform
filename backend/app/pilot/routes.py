"""Pilot API routes — registration, feedback, analytics, and assessment start."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session as DbSession
from sqlalchemy import func

from app.database import get_db
from app.auth.tenant_guard import require_role
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


# ── Protected Report (admin-only) ─────────────────

from app.models.task_run import TaskRun
from app.assessment.models import Assessment


@router.get("/report")
def pilot_report(
    db: DbSession = Depends(get_db),
    user: dict = Depends(require_role("admin")),
):
    """Full pilot report — admin only."""

    org = _get_pilot_org(db)

    # ── All participants ──
    participants = db.query(PilotParticipant).all()

    participant_reports = []
    for p in participants:
        candidate = db.query(Candidate).filter(Candidate.id == p.candidate_id).first()
        if not candidate:
            continue

        # Capability scores
        cap_scores = db.query(CandidateScore).filter(
            CandidateScore.candidate_id == p.candidate_id
        ).all()
        capabilities = {cs.capability: cs.score for cs in cap_scores}
        avg_score = round(sum(capabilities.values()) / len(capabilities), 1) if capabilities else 0

        # Task evaluations
        sessions = db.query(Session).filter(Session.candidate_id == p.candidate_id).all()
        session_ids = [s.id for s in sessions]
        task_runs = db.query(TaskRun).filter(TaskRun.session_id.in_(session_ids)).all() if session_ids else []

        task_details = []
        for tr in task_runs:
            eval_result = db.query(EvaluationResult).filter(
                EvaluationResult.task_run_id == tr.id
            ).first()
            task_details.append({
                "task_id": tr.task_id,
                "status": tr.status,
                "solution": tr.solution[:200] if tr.solution else None,
                "diagnostic_score": eval_result.diagnostic_score if eval_result else None,
                "success_score": eval_result.success_score if eval_result else None,
                "efficiency_score": eval_result.efficiency_score if eval_result else None,
                "iteration_score": eval_result.iteration_score if eval_result else None,
                "simulation_runs": eval_result.simulation_runs if eval_result else None,
            })

        # Feedback
        feedback = db.query(PilotFeedback).filter(
            PilotFeedback.candidate_id == p.candidate_id
        ).first()
        feedback_data = None
        if feedback:
            feedback_data = {
                "task_realism": feedback.task_realism,
                "instruction_clarity": feedback.instruction_clarity,
                "evaluation_fairness": feedback.evaluation_fairness,
                "difficulty": feedback.difficulty,
                "overall_experience": feedback.overall_experience,
                "feedback_text": feedback.feedback_text,
            }

        participant_reports.append({
            "candidate_id": p.candidate_id,
            "name": candidate.name,
            "email": p.email,
            "years_experience": p.years_experience,
            "primary_role": p.primary_role,
            "llm_experience_level": p.llm_experience_level,
            "company": p.company,
            "registered_at": str(p.created_at) if p.created_at else None,
            "capabilities": capabilities,
            "avg_score": avg_score,
            "tasks": task_details,
            "feedback": feedback_data,
        })

    # ── Aggregates ──
    all_scores = [p["avg_score"] for p in participant_reports if p["avg_score"] > 0]
    all_feedback = [p["feedback"] for p in participant_reports if p["feedback"]]

    avg_feedback_agg = {}
    for field in ["task_realism", "difficulty", "evaluation_fairness",
                   "instruction_clarity", "overall_experience"]:
        vals = [f[field] for f in all_feedback if f.get(field)]
        avg_feedback_agg[field] = round(sum(vals) / len(vals), 1) if vals else None

    role_breakdown = {}
    for p in participant_reports:
        role = p["primary_role"] or "Unknown"
        role_breakdown.setdefault(role, []).append(p["avg_score"])

    return {
        "summary": {
            "total_participants": len(participant_reports),
            "avg_score": round(sum(all_scores) / len(all_scores), 1) if all_scores else 0,
            "score_range": {
                "min": min(all_scores) if all_scores else 0,
                "max": max(all_scores) if all_scores else 0,
            },
            "feedback_responses": len(all_feedback),
            "avg_feedback": avg_feedback_agg,
            "by_role": {k: round(sum(v)/len(v), 1) for k, v in role_breakdown.items() if v},
        },
        "participants": participant_reports,
    }

