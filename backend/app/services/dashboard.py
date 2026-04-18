from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.evaluation_result import EvaluationResult
from app.models.scoring_result import ScoringResult
from app.models.simulation_run import SimulationRun
from app.models.task_run import TaskRun
from app.services.candidates import get_candidate, list_candidates
from app.services.telemetry import list_task_run_events


def get_dashboard_candidates(db: Session, organization_id: str):
    return list_candidates(db, organization_id)


def get_candidate_dashboard_profile(db: Session, organization_id: str, candidate_id: str) -> dict:
    candidate = get_candidate(db, organization_id, candidate_id)
    latest_score = db.scalar(
        select(ScoringResult)
        .where(
            ScoringResult.organization_id == organization_id,
            ScoringResult.candidate_id == candidate_id,
        )
        .order_by(ScoringResult.created_at.desc())
    )
    assessments = list(
        db.scalars(
            select(Assessment).where(
                Assessment.organization_id == organization_id,
                Assessment.candidate_id == candidate_id,
            )
        )
    )
    return {
        "candidate": candidate,
        "score": latest_score,
        "assessments": assessments,
    }


def get_candidate_task_runs(db: Session, organization_id: str, candidate_id: str) -> list[dict]:
    task_runs = list(
        db.scalars(
            select(TaskRun)
            .where(
                TaskRun.organization_id == organization_id,
                TaskRun.candidate_id == candidate_id,
            )
            .order_by(TaskRun.started_at.asc())
        )
    )
    evaluations = {
        item.task_run_id: item
        for item in db.scalars(
            select(EvaluationResult).where(
                EvaluationResult.organization_id == organization_id,
                EvaluationResult.candidate_id == candidate_id,
            )
        )
    }
    simulations: dict[str, SimulationRun] = {}
    for item in db.scalars(
        select(SimulationRun)
        .where(
            SimulationRun.organization_id == organization_id,
            SimulationRun.candidate_id == candidate_id,
        )
        .order_by(SimulationRun.created_at.desc())
    ):
        simulations.setdefault(item.task_run_id, item)
    results: list[dict] = []
    for task_run in task_runs:
        evaluation = evaluations.get(task_run.id)
        simulation = simulations.get(task_run.id)
        results.append(
            {
                "task_run": task_run,
                "evaluation": evaluation,
                "latest_simulation": simulation,
            }
        )
    return results


def get_session_replay(db: Session, organization_id: str, task_run_id: str) -> dict:
    events = list_task_run_events(db, organization_id, task_run_id)
    simulation_runs = list(
        db.scalars(
            select(SimulationRun)
            .where(
                SimulationRun.organization_id == organization_id,
                SimulationRun.task_run_id == task_run_id,
            )
            .order_by(SimulationRun.created_at.asc())
        )
    )
    evaluation = db.scalar(
        select(EvaluationResult).where(
            EvaluationResult.organization_id == organization_id,
            EvaluationResult.task_run_id == task_run_id,
        )
    )
    return {
        "events": events,
        "simulation_runs": simulation_runs,
        "evaluation": evaluation,
    }
