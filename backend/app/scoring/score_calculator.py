"""Task score calculator.

Applies the scoring model weights to evaluation dimension scores,
producing a single 0–100 task score.
"""

from app.scoring.scoring_model import DIMENSION_WEIGHTS


def calculate_task_score(
    diagnostic_score: float,
    success_score: float,
    efficiency_score: float,
    iteration_score: float,
) -> float:
    """Compute a weighted task score from evaluation dimensions.

    Args:
        diagnostic_score:  0–1
        success_score:     0–1
        efficiency_score:  0–1
        iteration_score:   0–1

    Returns:
        Task score on a 0–100 scale, rounded to 1 decimal.
    """
    raw = (
        DIMENSION_WEIGHTS["diagnostic_score"] * diagnostic_score
        + DIMENSION_WEIGHTS["success_score"] * success_score
        + DIMENSION_WEIGHTS["efficiency_score"] * efficiency_score
        + DIMENSION_WEIGHTS["iteration_score"] * iteration_score
    )
    return round(raw * 100, 1)


def calculate_task_score_from_result(evaluation_result) -> float:
    """Convenience wrapper that accepts an EvaluationResult ORM object."""
    return calculate_task_score(
        diagnostic_score=evaluation_result.diagnostic_score,
        success_score=evaluation_result.success_score,
        efficiency_score=evaluation_result.efficiency_score,
        iteration_score=evaluation_result.iteration_score,
    )
