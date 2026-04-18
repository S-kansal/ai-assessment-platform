from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import AuthContext, envelope, get_current_user, get_db
from app.schemas.telemetry_event import TelemetryCreateRequest
from app.services.tasks import get_task_run
from app.services.telemetry import create_telemetry_event, list_task_run_events
from app.core.dependencies import require_candidate_self


router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.post("")
def create_telemetry_route(
    body: TelemetryCreateRequest,
    user: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    task_run = get_task_run(db, user.organization_id, body.task_run_id)
    require_candidate_self(task_run.candidate_id, user)
    event = create_telemetry_event(
        db,
        user.organization_id,
        body.task_run_id,
        body.event_type,
        body.monotonic_timestamp_ms,
        body.payload,
    )
    db.commit()
    return envelope({"id": event.id, "status": "recorded"})


@router.get("/{task_run_id}")
def get_telemetry_route(
    task_run_id: str,
    user: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    task_run = get_task_run(db, user.organization_id, task_run_id)
    require_candidate_self(task_run.candidate_id, user)
    events = list_task_run_events(db, user.organization_id, task_run_id)
    return envelope(
        [
            {
                "id": event.id,
                "event_type": event.event_type,
                "monotonic_timestamp_ms": event.monotonic_timestamp_ms,
                "payload": event.payload,
                "created_at": event.created_at.isoformat(),
            }
            for event in events
        ]
    )
