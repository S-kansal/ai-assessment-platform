"""Scoring model — defines how evaluation dimensions combine into a task score.

Formula:
    task_score = 0.40 * diagnostic_score
               + 0.30 * success_score
               + 0.20 * efficiency_score
               + 0.10 * iteration_score

Rationale:
    - Diagnosis is the hardest and most valuable skill (40%)
    - Producing a correct solution is next (30%)
    - Efficiency in reaching the solution matters (20%)
    - Iteration/debugging style contributes least (10%)

All input scores are 0–1; the output task_score is 0–100.
"""

# Weights must sum to 1.0
DIMENSION_WEIGHTS = {
    "diagnostic_score": 0.40,
    "success_score": 0.30,
    "efficiency_score": 0.20,
    "iteration_score": 0.10,
}
