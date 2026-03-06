"""Celery worker configuration for background jobs.

Workers handle:
- evaluation pipeline execution
- scoring aggregation
- analytics generation
- report generation

Requires Redis as the message broker:
    REDIS_URL=redis://localhost:6379/0

Start worker:
    celery -A app.core.celery_app worker --loglevel=info
"""

import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "ai_assessment",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minute hard limit
    task_soft_time_limit=240,  # 4 minute soft limit
)


# ── Example background tasks ──────────────────────
@celery_app.task(name="run_evaluation")
def run_evaluation_task(task_run_id: str):
    """Run evaluation pipeline asynchronously."""
    from app.database import SessionLocal
    from app.evaluation.evaluator import evaluate_task_run

    db = SessionLocal()
    try:
        evaluate_task_run(db, task_run_id)
    finally:
        db.close()


@celery_app.task(name="compute_scores")
def compute_scores_task(candidate_id: str):
    """Compute candidate capability scores asynchronously."""
    from app.database import SessionLocal
    from app.scoring.scoring_service import compute_candidate_scores

    db = SessionLocal()
    try:
        compute_candidate_scores(db, candidate_id)
    finally:
        db.close()
