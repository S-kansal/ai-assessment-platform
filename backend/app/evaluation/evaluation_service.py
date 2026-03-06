"""Evaluation service — high-level interface consumed by API routes.

Wraps the evaluator core and provides error handling for the route layer.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session as DbSession

from app.evaluation.evaluator import evaluate_task_run


def run_evaluation(db: DbSession, task_run_id: str) -> dict:
    """Trigger evaluation for a task run and return structured results.

    Raises HTTPException on errors so routes get proper HTTP responses.
    """
    try:
        return evaluate_task_run(db, task_run_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
