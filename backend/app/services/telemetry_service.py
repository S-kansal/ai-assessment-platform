from sqlalchemy.orm import Session as DbSession

from app.models.session import Session
from app.models.telemetry import TelemetryEvent


def create_telemetry_event(
    db: DbSession,
    session_id: str,
    task_id: str,
    event_type: str,
    payload: dict,
) -> TelemetryEvent:
    """Validate and persist a telemetry event to the database.

    Resolves organization_id from the session so events are always
    correctly scoped to the owning tenant.
    """
    session = db.query(Session).filter(Session.id == session_id).first()
    org_id = session.organization_id if session else None

    event = TelemetryEvent(
        session_id=session_id,
        task_id=task_id,
        event_type=event_type,
        payload_json=payload,
        organization_id=org_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
