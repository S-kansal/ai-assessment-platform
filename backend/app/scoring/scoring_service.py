"""Scoring service — orchestrates the full scoring pipeline.

Pipeline:
1. Load all sessions for a candidate
2. Load evaluation results for each session's task runs
3. Calculate task scores using the scoring model
4. Map tasks to capabilities
5. Aggregate per-capability scores
6. Store task_scores + candidate_scores records
7. Return structured capability profile
"""

from typing import Dict, List

from fastapi import HTTPException
from sqlalchemy.orm import Session as DbSession

from app.models.candidate import Candidate
from app.models.session import Session
from app.models.task_run import TaskRun
from app.evaluation.models import EvaluationResult
from app.scoring.models import CandidateScore, TaskScore
from app.scoring.score_calculator import calculate_task_score_from_result
from app.scoring.score_aggregator import aggregate_capability_scores
from app.scoring.capability_map import get_capability_for_task
from app.models.assessment_result import AssessmentResult


def compute_candidate_scores(db: DbSession, candidate_id: str) -> Dict:
    """Compute and store capability scores for a candidate.

    Returns a structured capability profile.
    """
    # --- Validate candidate ---
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # --- Load all sessions for this candidate ---
    sessions = db.query(Session).filter(Session.candidate_id == candidate_id).all()
    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions found for candidate")

    session_ids = [s.id for s in sessions]

    # --- Load all task runs across sessions ---
    task_runs = (
        db.query(TaskRun)
        .filter(TaskRun.session_id.in_(session_ids))
        .all()
    )
    if not task_runs:
        raise HTTPException(status_code=404, detail="No task runs found for candidate")

    task_run_ids = [tr.id for tr in task_runs]

    # --- Load evaluation results ---
    eval_results = (
        db.query(EvaluationResult)
        .filter(EvaluationResult.task_run_id.in_(task_run_ids))
        .all()
    )
    if not eval_results:
        raise HTTPException(
            status_code=404,
            detail="No evaluation results found — run evaluations first",
        )

    # --- Build task_run_id → task_id lookup ---
    run_to_task = {tr.id: tr.task_id for tr in task_runs}

    # --- Calculate per-task scores and persist ---
    task_scores: List[Dict] = []
    for er in eval_results:
        task_id = run_to_task.get(er.task_run_id)
        if not task_id:
            continue

        score = calculate_task_score_from_result(er)
        cap_mapping = get_capability_for_task(task_id)
        capability = cap_mapping["capability"] if cap_mapping else None

        task_scores.append({
            "task_id": task_id,
            "task_run_id": er.task_run_id,
            "task_score": score,
        })

        # Persist task score (upsert)
        existing_ts = (
            db.query(TaskScore)
            .filter(TaskScore.task_run_id == er.task_run_id)
            .first()
        )
        if existing_ts:
            existing_ts.task_score = score
            existing_ts.capability = capability
        else:
            db.add(TaskScore(
                task_run_id=er.task_run_id,
                task_id=task_id,
                task_score=score,
                capability=capability,
            ))

    # --- Aggregate by capability ---
    capability_data = aggregate_capability_scores(task_scores)

    # --- Store candidate_scores (upsert per capability) ---
    capabilities_flat: Dict[str, float] = {}
    for capability, info in capability_data.items():
        cap_score = info["score"]
        sample_size = info["sample_size"]
        capabilities_flat[capability] = cap_score

        existing = (
            db.query(CandidateScore)
            .filter(
                CandidateScore.candidate_id == candidate_id,
                CandidateScore.capability == capability,
            )
            .first()
        )
        if existing:
            existing.score = cap_score
            existing.sample_size = sample_size
        else:
            db.add(CandidateScore(
                candidate_id=candidate_id,
                capability=capability,
                score=cap_score,
                sample_size=sample_size,
            ))

    db.commit()

    # --- Store assessment result snapshot ---
    eval_scores = [er.efficiency_score for er in eval_results]
    evaluation_summary = {
        "tasks_completed": len(eval_results),
        "avg_efficiency": round(sum(eval_scores) / len(eval_scores), 2) if eval_scores else 0,
        "task_scores": [{"task_id": ts["task_id"], "score": ts["task_score"]} for ts in task_scores],
    }

    existing_ar = (
        db.query(AssessmentResult)
        .filter(
            AssessmentResult.candidate_id == candidate_id,
            AssessmentResult.session_id == session_ids[0],
        )
        .first()
    )
    if existing_ar:
        existing_ar.capability_profile = capabilities_flat
        existing_ar.evaluation_summary = evaluation_summary
    else:
        db.add(AssessmentResult(
            candidate_id=candidate_id,
            session_id=session_ids[0],
            capability_profile=capabilities_flat,
            evaluation_summary=evaluation_summary,
        ))
    db.commit()

    return {
        "candidate_id": candidate_id,
        "capabilities": capabilities_flat,
        "task_scores": task_scores,
    }

