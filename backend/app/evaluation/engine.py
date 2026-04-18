from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.evaluation.dimensions import (
    diagnostic_accuracy,
    efficiency,
    iteration_quality,
    solution_success,
)
from app.evaluation.rules import check_success
from app.models.evaluation_result import EvaluationResult
from app.models.simulation_run import SimulationRun
from app.models.task import Task
from app.models.task_run import TaskRun
from app.models.telemetry_event import TelemetryEvent


def _as_utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def evaluate_task_run(db: Session, task_run: TaskRun, task: Task) -> EvaluationResult:
    simulation_runs = list(
        db.scalars(
            select(SimulationRun)
            .where(
                SimulationRun.task_run_id == task_run.id,
                SimulationRun.organization_id == task_run.organization_id,
            )
            .order_by(SimulationRun.created_at.asc())
        )
    )
    telemetry_events = list(
        db.scalars(
            select(TelemetryEvent)
            .where(
                TelemetryEvent.task_run_id == task_run.id,
                TelemetryEvent.organization_id == task_run.organization_id,
            )
            .order_by(TelemetryEvent.monotonic_timestamp_ms.asc())
        )
    )

    if task_run.completed_at is None:
        task_run.completed_at = datetime.now(timezone.utc)

    successful_runs = sum(
        1 for run in simulation_runs if check_success(task.id, run.response_text)
    )
    final_response_text = simulation_runs[-1].response_text if simulation_runs else ""
    completed_at = _as_utc(task_run.completed_at)
    started_at = _as_utc(task_run.started_at)
    elapsed_minutes = max(((completed_at - started_at).total_seconds() / 60.0), 0.0)
    prompt_edits = sum(1 for event in telemetry_events if event.event_type == "prompt_edit")
    log_inspections = sum(
        1
        for event in telemetry_events
        if event.event_type in {"log_inspection", "retrieval_inspection", "simulation_output_view"}
    )

    dimension_scores = {
        "diagnostic_accuracy": diagnostic_accuracy(
            task_run.submitted_root_cause or "",
            task.failure_modes,
        ),
        "solution_success": solution_success(
            check_success(task.id, final_response_text)
        ),
        "efficiency": efficiency(
            elapsed_minutes,
            len(simulation_runs),
            int(task.scoring_rubric.get("target_minutes", 10)),
            int(task.scoring_rubric.get("target_simulation_runs", 3)),
        ),
        "iteration_quality": iteration_quality(
            successful_runs,
            len(simulation_runs),
            prompt_edits,
            log_inspections,
        ),
    }

    formulas = {
        "diagnostic_accuracy": {
            "formula": "matched_expected_failure_modes / expected_failure_modes",
            "expected_failure_modes": len(task.failure_modes),
        },
        "solution_success": {
            "formula": "1 if final_simulation_run_meets_success_criteria else 0",
        },
        "efficiency": {
            "formula": "0.5*(1-min(elapsed_minutes/target_minutes,1)) + 0.5*(1-min(max(simulation_runs-target_runs,0)/target_runs,1))",
            "elapsed_minutes": round(elapsed_minutes, 2),
            "simulation_runs": len(simulation_runs),
            "target_minutes": int(task.scoring_rubric.get("target_minutes", 10)),
            "target_simulation_runs": int(task.scoring_rubric.get("target_simulation_runs", 3)),
        },
        "iteration_quality": {
            "formula": "0.5*(successful_runs/simulation_runs) + 0.25*edit_discipline + 0.25*evidence_usage",
            "successful_runs": successful_runs,
            "simulation_runs": len(simulation_runs),
            "prompt_edits": prompt_edits,
            "log_inspections": log_inspections,
        },
    }
    evidence = {
        "final_response_text": final_response_text,
        "simulation_run_ids": [run.id for run in simulation_runs],
        "telemetry_event_ids": [event.id for event in telemetry_events],
    }
    total_score = round(sum(dimension_scores.values()) / len(dimension_scores), 4)

    evaluation = db.scalar(
        select(EvaluationResult).where(EvaluationResult.task_run_id == task_run.id)
    )
    if evaluation is None:
        evaluation = EvaluationResult(
            organization_id=task_run.organization_id,
            assessment_id=task_run.assessment_id,
            task_run_id=task_run.id,
            candidate_id=task_run.candidate_id,
        )
        db.add(evaluation)

    evaluation.dimension_scores = dimension_scores
    evaluation.formulas = formulas
    evaluation.evidence = evidence
    evaluation.total_score = total_score
    db.flush()
    return evaluation


def get_evaluation_or_raise(
    db: Session,
    organization_id: str,
    task_run_id: str,
) -> EvaluationResult:
    evaluation = db.scalar(
        select(EvaluationResult).where(
            EvaluationResult.task_run_id == task_run_id,
            EvaluationResult.organization_id == organization_id,
        )
    )
    if evaluation is None:
        raise NotFoundError("Evaluation result not found")
    return evaluation
