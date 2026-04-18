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
    task_time_limit=300,
    task_soft_time_limit=240,
)
