from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.telemetry_event import TelemetryEvent
from app.models.task_run import TaskRun
from app.models.assessment import Assessment
from app.core.exceptions import NotFoundError, ValidationError


ALLOWED_TELEMETRY_EVENTS = {
    "prompt_edit",
    "prompt_submitted",
    "query_submit",
    "simulation_output_view",
    "log_inspection",
    "retrieval_inspection",
    "solution_submit",
    "task_started",
    "simulation_run",
}


def create_telemetry_event(
    db: Session,
    organization_id: str,
    task_run_id: str,
    event_type: str,
    monotonic_timestamp_ms: int,
    payload: dict,
) -> TelemetryEvent:
    if event_type not in ALLOWED_TELEMETRY_EVENTS:
        raise ValidationError("Unsupported telemetry event type")
    task_run = db.scalar(
        select(TaskRun).where(
            TaskRun.id == task_run_id,
            TaskRun.organization_id == organization_id,
        )
    )
    if task_run is None:
        raise NotFoundError("Task run not found")
    assessment = db.scalar(
        select(Assessment).where(
            Assessment.id == task_run.assessment_id,
            Assessment.organization_id == organization_id,
        )
    )
    if assessment is None:
        raise NotFoundError("Assessment not found")

    last_event = db.scalar(
        select(TelemetryEvent)
        .where(
            TelemetryEvent.organization_id == organization_id,
            TelemetryEvent.task_run_id == task_run_id,
        )
        .order_by(TelemetryEvent.monotonic_timestamp_ms.desc())
    )
    normalized_timestamp = (
        monotonic_timestamp_ms
        if last_event is None
        else max(monotonic_timestamp_ms, last_event.monotonic_timestamp_ms + 1)
    )

    event = TelemetryEvent(
        organization_id=organization_id,
        assessment_id=task_run.assessment_id,
        task_run_id=task_run.id,
        candidate_id=task_run.candidate_id,
        session_id=assessment.browser_session_id,
        event_type=event_type,
        monotonic_timestamp_ms=normalized_timestamp,
        payload=payload,
    )
    db.add(event)
    db.flush()
    return event


def list_task_run_events(
    db: Session,
    organization_id: str,
    task_run_id: str,
) -> list[TelemetryEvent]:
    return list(
        db.scalars(
            select(TelemetryEvent)
            .where(
                TelemetryEvent.organization_id == organization_id,
                TelemetryEvent.task_run_id == task_run_id,
            )
            .order_by(TelemetryEvent.monotonic_timestamp_ms.asc())
        )
    )
