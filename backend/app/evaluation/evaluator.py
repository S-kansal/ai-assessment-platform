"""Evaluator core — orchestrates the full evaluation pipeline.

Pipeline:
1. Load task_run + task configuration
2. Load telemetry events for the task run
3. Extract behavioural metrics from telemetry
4. Apply evaluation rules
5. Compute scores
6. Store evaluation result
7. Return scores + debug log
"""

from typing import Dict, List

from sqlalchemy.orm import Session as DbSession

from app.models.task_run import TaskRun
from app.models.task import Task
from app.models.telemetry import TelemetryEvent
from app.evaluation.models import EvaluationResult
from app.evaluation.metrics import extract_metrics
from app.evaluation import rules


def evaluate_task_run(db: DbSession, task_run_id: str) -> Dict:
    """Run the full evaluation pipeline for a completed task run.

    Returns a dict with scores and debug information.
    """
    debug_log: List[str] = []

    # --- Step 1: Load task_run ---
    task_run = db.query(TaskRun).filter(TaskRun.id == task_run_id).first()
    if not task_run:
        raise ValueError(f"Task run '{task_run_id}' not found")

    debug_log.append(f"Loaded task_run: {task_run_id} (status={task_run.status})")

    # --- Step 2: Load task configuration ---
    task = db.query(Task).filter(Task.id == task_run.task_id).first()
    if not task:
        raise ValueError(f"Task '{task_run.task_id}' not found")

    failure_mode = task.failure_mode or "unknown"
    debug_log.append(f"Task: {task.name} (failure_mode={failure_mode})")

    # --- Step 3: Load telemetry events ---
    telemetry_rows = (
        db.query(TelemetryEvent)
        .filter(TelemetryEvent.session_id == task_run.session_id)
        .order_by(TelemetryEvent.timestamp)
        .all()
    )

    # Convert ORM objects to dicts for metrics extraction
    events = [
        {
            "event_type": row.event_type,
            "timestamp": row.timestamp,
            "payload_json": row.payload_json,
            "task_id": row.task_id,
        }
        for row in telemetry_rows
    ]

    debug_log.append(f"Telemetry events loaded: {len(events)}")

    # --- Step 4: Extract metrics ---
    metrics = extract_metrics(events)
    debug_log.append(
        f"Metrics: runs={metrics['simulation_runs']}, "
        f"edits={metrics['prompt_edits']}, "
        f"inspections={metrics['retrieval_inspections']}, "
        f"time={metrics['time_to_solution']:.0f}s"
    )

    # --- Step 5: Apply evaluation rules ---
    solution = task_run.solution

    diagnostic_score = rules.score_diagnostic(failure_mode, solution, metrics)
    debug_log.append(f"Diagnostic score: {diagnostic_score}")

    success_score = rules.score_success(solution, events)
    debug_log.append(f"Success score: {success_score}")

    efficiency_score = rules.score_efficiency(metrics)
    debug_log.append(f"Efficiency score: {efficiency_score}")

    iteration_score = rules.score_iteration(metrics)
    debug_log.append(f"Iteration score: {iteration_score}")

    # --- Step 6: Build evaluation trace ---
    evaluation_trace = {
        "failure_mode": failure_mode,
        "solution_keywords_matched": diagnostic_score == 1.0,
        "simulation_runs": metrics["simulation_runs"],
        "prompt_edits": metrics["prompt_edits"],
        "retrieval_inspections": metrics["retrieval_inspections"],
        "inspection_before_edit": metrics.get("inspected_before_edit", False),
        "time_to_solution": metrics["time_to_solution"],
        "total_events": metrics["total_events"],
    }

    task_type = task.task_type if hasattr(task, "task_type") else None

    # --- Step 7: Store evaluation result ---
    existing = (
        db.query(EvaluationResult)
        .filter(EvaluationResult.task_run_id == task_run_id)
        .first()
    )
    fields = dict(
        diagnostic_score=diagnostic_score,
        success_score=success_score,
        efficiency_score=efficiency_score,
        iteration_score=iteration_score,
        simulation_runs=metrics["simulation_runs"],
        prompt_edits=metrics["prompt_edits"],
        retrieval_inspections=metrics["retrieval_inspections"],
        time_to_solution=metrics["time_to_solution"],
        evaluation_trace=evaluation_trace,
        task_type=task_type,
    )
    if existing:
        for k, v in fields.items():
            setattr(existing, k, v)
    else:
        result = EvaluationResult(task_run_id=task_run_id, **fields)
        db.add(result)

    db.commit()
    debug_log.append("Evaluation result stored")

    # --- Step 8: Return scores ---
    return {
        "task_run_id": task_run_id,
        "diagnostic_score": diagnostic_score,
        "success_score": success_score,
        "efficiency_score": efficiency_score,
        "iteration_score": iteration_score,
        "debug_log": debug_log,
    }
