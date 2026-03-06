from sqlalchemy.orm import Session as DbSession

from app.models.telemetry import TelemetryEvent


def create_telemetry_event(
    db: DbSession,
    session_id: str,
    task_id: str,
    event_type: str,
    payload: dict,
) -> TelemetryEvent:
    """Validate and persist a telemetry event to the database.

    This service is the single entry point for writing telemetry data.
    It will be consumed by routes, and later by the simulation engine
    and evaluation engine.
    """
    event = TelemetryEvent(
        session_id=session_id,
        task_id=task_id,
        event_type=event_type,
        payload_json=payload,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
