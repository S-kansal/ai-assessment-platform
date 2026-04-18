from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import (
    AuthContext,
    envelope,
    get_current_user,
    get_db,
    rate_limit_dependency,
    require_candidate_self,
)
from app.core.config import settings
from app.schemas.simulation_run import SimulationRequest
from app.services.simulations import create_simulation_run
from app.services.tasks import get_task, get_task_run
from app.services.telemetry import create_telemetry_event


router = APIRouter(prefix="/simulations", tags=["simulations"])


@router.post("/run", dependencies=[Depends(rate_limit_dependency("simulations", settings.request_rate_limit_per_minute))])
def run_simulation_route(
    body: SimulationRequest,
    user: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    task_run = get_task_run(db, user.organization_id, body.task_run_id)
    require_candidate_self(task_run.candidate_id, user)
    task = get_task(db, user.organization_id, task_run.task_id)
    simulation_run = create_simulation_run(db, task_run, task, body.prompt_text, body.query_text)
    create_telemetry_event(
        db,
        user.organization_id,
        body.task_run_id,
        "simulation_run",
        int(simulation_run.created_at.timestamp() * 1000),
        {
            "query_text": body.query_text,
            "prompt_text": body.prompt_text,
            "simulation_run_id": simulation_run.id,
        },
    )
    db.commit()
    return envelope(
        {
            "id": simulation_run.id,
            "task_run_id": simulation_run.task_run_id,
            "prompt_text": simulation_run.prompt_text,
            "query_text": simulation_run.query_text,
            "retrieved_chunks": simulation_run.retrieved_chunks,
            "debug_logs": simulation_run.debug_logs,
            "response_text": simulation_run.response_text,
            "output_quality": simulation_run.output_quality,
            "confidence_score": simulation_run.confidence_score,
            "created_at": simulation_run.created_at.isoformat(),
        }
    )
