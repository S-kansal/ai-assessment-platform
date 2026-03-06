from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from app.database import get_db
from app.models.task_run import TaskRun
from app.models.task import Task
from app.services.telemetry_service import create_telemetry_event
from app.simulation.rag_state import RAGState
from app.simulation.rag_simulator import run_rag_pipeline
from app.core.logging import get_logger
from app.core.rate_limit import limiter

router = APIRouter()
logger = get_logger("simulation")


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class RAGSimulationRequest(BaseModel):
    task_run_id: str
    query: str
    prompt_template: str = "Use the provided context to answer the question."
    failure_mode: Optional[str] = None  # explicit override


class RAGSimulationResponse(BaseModel):
    retrieved_chunks: list
    generated_answer: str
    debug_logs: list


# ---------------------------------------------------------------------------
# POST /simulate/rag
# ---------------------------------------------------------------------------

@router.post("/simulate/rag", response_model=RAGSimulationResponse)
@limiter.limit("30/minute")
def simulate_rag(
    request: Request,
    body: RAGSimulationRequest,
    db: DbSession = Depends(get_db),
):
    """Run a deterministic RAG simulation and log the telemetry event.

    The failure mode is resolved in this order:
    1. Explicit override in the request body
    2. Looked up from the task_run → task → failure_mode in the database
    3. Fallback default: 'irrelevant_retrieval'
    """

    failure_mode = body.failure_mode
    session_id = None

    # --- Resolve failure mode from task_run if not explicitly set ---
    if failure_mode is None:
        task_run = (
            db.query(TaskRun).filter(TaskRun.id == body.task_run_id).first()
        )
        if task_run:
            session_id = task_run.session_id
            task = db.query(Task).filter(Task.id == task_run.task_id).first()
            if task and task.failure_mode:
                failure_mode = task.failure_mode

    # --- Default fallback ---
    if failure_mode is None:
        failure_mode = "irrelevant_retrieval"

    # --- Initialise simulation state ---
    state = RAGState(
        failure_mode=failure_mode,
        prompt_template=body.prompt_template,
    )

    # --- Run the deterministic pipeline ---
    result = run_rag_pipeline(
        query=body.query,
        prompt_template=body.prompt_template,
        state=state,
    )

    # --- Log telemetry event ---
    create_telemetry_event(
        db=db,
        session_id=session_id or body.task_run_id,
        task_id=body.task_run_id,
        event_type="test_run",
        payload={
            "query": body.query,
            "prompt_template": body.prompt_template,
            "failure_mode": failure_mode,
            "generated_answer": result["generated_answer"],
        },
    )

    return RAGSimulationResponse(
        retrieved_chunks=result["retrieved_chunks"],
        generated_answer=result["generated_answer"],
        debug_logs=result["debug_logs"],
    )
