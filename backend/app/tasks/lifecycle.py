from datetime import datetime, timedelta, timezone

from app.core.config import settings


ACTIVE_TASK_STATES = {"pending", "active"}
TERMINAL_TASK_STATES = {"completed", "timed_out", "abandoned"}


def get_assessment_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(
        minutes=settings.assessment_timeout_minutes
    )


def start_status() -> str:
    return "active"


def complete_status() -> str:
    return "completed"


def timeout_status() -> str:
    return "timed_out"
