from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from app.database import get_db
from app.services.telemetry_service import create_telemetry_event

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class TelemetryCreateRequest(BaseModel):
    session_id: str
    task_id: str
    event_type: str
    payload: Dict[str, Any] = {}


class TelemetryCreateResponse(BaseModel):
    event_id: str
    status: str = "recorded"


# ---------------------------------------------------------------------------
# POST /telemetry
# ---------------------------------------------------------------------------

@router.post("/telemetry", response_model=TelemetryCreateResponse)
def log_telemetry_event(
    body: TelemetryCreateRequest,
    db: DbSession = Depends(get_db),
):
    """Record a candidate telemetry event."""
    event = create_telemetry_event(
        db=db,
        session_id=body.session_id,
        task_id=body.task_id,
        event_type=body.event_type,
        payload=body.payload,
    )
    return TelemetryCreateResponse(event_id=event.id)
