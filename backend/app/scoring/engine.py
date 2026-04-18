from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.evaluation_result import EvaluationResult
from app.models.scoring_result import ScoringResult
from app.models.task_run import TaskRun
from app.scoring.capabilities import CAPABILITY_DIMENSIONS
from app.scoring.weights import ASSESSMENT_CAPABILITY_WEIGHTS, WEIGHTING_VERSION
from app.evaluation.rules import canonical_task_id


def compute_scoring_result(
    db: Session,
    assessment_id: str,
    organization_id: str,
) -> ScoringResult:
    task_runs = list(
        db.scalars(
            select(TaskRun).where(
                TaskRun.assessment_id == assessment_id,
                TaskRun.organization_id == organization_id,
            )
        )
    )
    if not task_runs:
        raise NotFoundError("Assessment task runs not found")

    evaluations = list(
        db.scalars(
            select(EvaluationResult).where(
                EvaluationResult.assessment_id == assessment_id,
                EvaluationResult.organization_id == organization_id,
            )
        )
    )
    evaluation_by_task_run = {evaluation.task_run_id: evaluation for evaluation in evaluations}
    task_run_by_id = {task_run.id: task_run for task_run in task_runs}

    raw_scores: dict[str, float] = {}
    normalized_scores: dict[str, float] = {}
    for capability, config in CAPABILITY_DIMENSIONS.items():
        contributing_scores: list[float] = []
        for task_run_id, evaluation in evaluation_by_task_run.items():
            task_run = task_run_by_id[task_run_id]
            if canonical_task_id(task_run.task_id) not in config["tasks"]:
                continue
            score = sum(
                evaluation.dimension_scores.get(dimension, 0.0) * weight
                for dimension, weight in config["weights"].items()
            )
            contributing_scores.append(score * 100.0)
        raw = round(sum(contributing_scores) / len(contributing_scores), 2) if contributing_scores else 0.0
        raw_scores[capability] = raw
        normalized_scores[capability] = round(raw / 100.0, 4)

    aggregate_score = round(
        sum(
            raw_scores.get(capability, 0.0) * weight
            for capability, weight in ASSESSMENT_CAPABILITY_WEIGHTS.items()
        ),
        2,
    )

    scoring = db.scalar(
        select(ScoringResult).where(
            ScoringResult.assessment_id == assessment_id,
            ScoringResult.organization_id == organization_id,
        )
    )
    candidate_id = task_runs[0].candidate_id
    if scoring is None:
        scoring = ScoringResult(
            organization_id=organization_id,
            assessment_id=assessment_id,
            candidate_id=candidate_id,
        )
        db.add(scoring)

    scoring.raw_scores = raw_scores
    scoring.normalized_scores = normalized_scores
    scoring.aggregate_score = aggregate_score
    scoring.weighting_version = WEIGHTING_VERSION
    db.flush()
    return scoring
