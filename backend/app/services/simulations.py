from sqlalchemy.orm import Session

from app.models.simulation_run import SimulationRun
from app.models.task import Task
from app.models.task_run import TaskRun
from app.simulation.engine import run_simulation


def create_simulation_run(
    db: Session,
    task_run: TaskRun,
    task: Task,
    prompt_text: str,
    query_text: str,
) -> SimulationRun:
    result = run_simulation(task.scenario_key, task.failure_modes, prompt_text, query_text)
    simulation_run = SimulationRun(
        organization_id=task_run.organization_id,
        assessment_id=task_run.assessment_id,
        task_run_id=task_run.id,
        candidate_id=task_run.candidate_id,
        prompt_text=prompt_text,
        query_text=query_text,
        retrieved_chunks=result.retrieved_chunks,
        debug_logs=result.debug_logs,
        response_text=result.response_text,
        output_quality=result.output_quality,
        confidence_score=result.confidence_score,
        seed=result.seed,
    )
    db.add(simulation_run)
    db.flush()
    return simulation_run
