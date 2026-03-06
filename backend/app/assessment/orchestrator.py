"""Assessment orchestrator — manages multi-task assessment lifecycle.

Flow:
1. start_assessment → create assessment, assign first task
2. advance_assessment → complete current task, assign next or finish
3. complete_assessment → mark done, trigger scoring
"""

from datetime import datetime, timezone
from typing import Dict, Optional

from sqlalchemy.orm import Session as DbSession
from fastapi import HTTPException

from app.assessment.models import Assessment, AssessmentTask
from app.assessment import assessment_service as svc
from app.tasks.task_service import start_task, finish_task
from app.evaluation.evaluator import evaluate_task_run
from app.evaluation.models import EvaluationResult
from app.scoring.scoring_service import compute_candidate_scores
from app.models.assessment_result import AssessmentResult


# ── Default task sequence for MVP ──────────────────────────────
DEFAULT_TASK_IDS = ["rag_debug_01", "rag_debug_02", "rag_debug_03"]


def start_assessment(db: DbSession, candidate_id: str, session_id: str,
                     task_ids: list = None, org_id: str = None) -> Dict:
    """Create an assessment and start the first task."""
    tasks = task_ids or DEFAULT_TASK_IDS

    assessment = svc.create_assessment(db, candidate_id, session_id, tasks, org_id=org_id)

    # Mark assessment as running
    now = datetime.now(timezone.utc)
    assessment.status = "running"
    assessment.started_at = now
    db.commit()

    # Start first task
    first_at = svc.get_next_pending_task(db, assessment.id)
    if not first_at:
        raise HTTPException(status_code=400, detail="No tasks in assessment")

    task_result = start_task(db, session_id, first_at.task_id)
    first_at.task_run_id = task_result["task_run_id"]
    first_at.status = "running"
    first_at.started_at = now
    db.commit()

    return {
        "assessment_id": assessment.id,
        "status": assessment.status,
        "first_task": first_at.task_id,
        "task_run_id": task_result["task_run_id"],
        "description": task_result["description"],
        "total_tasks": len(tasks),
        "current_task_index": 1,
    }


def advance_assessment(db: DbSession, assessment_id: str,
                       task_run_id: str, solution: str = None) -> Dict:
    """Complete current task, evaluate it, and advance to the next task.

    Returns the next task info or assessment completion status.
    """
    assessment = svc.get_assessment(db, assessment_id)
    if assessment.status != "running":
        raise HTTPException(status_code=400, detail="Assessment is not running")

    # Find the current running task
    current = svc.get_current_task(db, assessment_id)
    if not current:
        raise HTTPException(status_code=400, detail="No running task found")

    if current.task_run_id != task_run_id:
        raise HTTPException(status_code=400, detail="Task run ID mismatch")

    # Complete the task
    now = datetime.now(timezone.utc)
    finish_task(db, task_run_id, solution)
    current.status = "completed"
    current.completed_at = now
    db.commit()

    # Evaluate the task
    try:
        evaluate_task_run(db, task_run_id)
    except Exception:
        pass  # evaluation may fail gracefully

    # Check for next task
    all_tasks = svc.get_assessment_tasks(db, assessment_id)
    completed_count = sum(1 for t in all_tasks if t.status == "completed")
    total = len(all_tasks)

    next_at = svc.get_next_pending_task(db, assessment_id)
    if next_at:
        # Start next task
        task_result = start_task(db, assessment.session_id, next_at.task_id)
        next_at.task_run_id = task_result["task_run_id"]
        next_at.status = "running"
        next_at.started_at = now
        db.commit()

        return {
            "status": "next_task",
            "task_id": next_at.task_id,
            "task_run_id": task_result["task_run_id"],
            "description": task_result["description"],
            "completed_tasks": completed_count,
            "total_tasks": total,
            "current_task_index": completed_count + 1,
        }
    else:
        # All tasks done — complete assessment
        return _complete_assessment(db, assessment, all_tasks)


def _complete_assessment(db: DbSession, assessment: Assessment,
                         all_tasks: list) -> Dict:
    """Finalize assessment and trigger scoring."""
    now = datetime.now(timezone.utc)
    assessment.status = "completed"
    assessment.completed_at = now
    db.commit()

    # Trigger scoring aggregation
    try:
        scores = compute_candidate_scores(db, assessment.candidate_id)
    except Exception:
        scores = {}

    # Build evaluation summary from task runs
    eval_summary = {"tasks_completed": len(all_tasks), "task_details": []}
    for at in all_tasks:
        if at.task_run_id:
            ev = db.query(EvaluationResult).filter(
                EvaluationResult.task_run_id == at.task_run_id
            ).first()
            if ev:
                eval_summary["task_details"].append({
                    "task_id": at.task_id,
                    "diagnostic": ev.diagnostic_score,
                    "efficiency": ev.efficiency_score,
                })
    eff_scores = [d["efficiency"] for d in eval_summary["task_details"] if d.get("efficiency")]
    eval_summary["avg_efficiency"] = round(sum(eff_scores) / len(eff_scores), 2) if eff_scores else 0

    # Compute final_score as average of capabilities
    caps = scores.get("capabilities", {})
    final_score = round(sum(caps.values()) / len(caps), 1) if caps else 0

    # Store assessment result snapshot
    db.add(AssessmentResult(
        assessment_id=assessment.id,
        candidate_id=assessment.candidate_id,
        session_id=assessment.session_id,
        final_score=final_score,
        capability_profile=caps,
        evaluation_summary=eval_summary,
    ))
    db.commit()

    return {
        "status": "completed",
        "completed_tasks": len(all_tasks),
        "total_tasks": len(all_tasks),
        "scores": scores,
    }


def get_assessment_status(db: DbSession, assessment_id: str) -> Dict:
    """Get current assessment status including task progress."""
    assessment = svc.get_assessment(db, assessment_id)
    all_tasks = svc.get_assessment_tasks(db, assessment_id)

    completed = sum(1 for t in all_tasks if t.status == "completed")
    current = svc.get_current_task(db, assessment_id)

    tasks_detail = []
    for t in all_tasks:
        tasks_detail.append({
            "task_id": t.task_id,
            "task_run_id": t.task_run_id,
            "order_index": t.order_index,
            "status": t.status,
        })

    return {
        "assessment_id": assessment.id,
        "candidate_id": assessment.candidate_id,
        "status": assessment.status,
        "current_task": current.task_id if current else None,
        "current_task_run_id": current.task_run_id if current else None,
        "completed_tasks": completed,
        "total_tasks": len(all_tasks),
        "tasks": tasks_detail,
    }
