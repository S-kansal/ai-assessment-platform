"""Deterministic evaluation rules for MVP.

Each rule maps observable behaviour (metrics + solution + task config) to a
score on a 0–1 scale. Rules are intentionally simple and transparent so
that evaluation is explainable and auditable.
"""

from typing import Dict, List


# =========================================================================
# Rule 1 — Diagnostic Accuracy
# =========================================================================

# Keywords that indicate the candidate identified the root cause, keyed by
# the task's failure_mode.
DIAGNOSTIC_KEYWORDS = {
    "irrelevant_retrieval": [
        "retrieval", "retrieve", "ranking", "embedding", "similarity",
        "search", "wrong document", "irrelevant",
    ],
    "incorrect_chunking": [
        "chunk", "chunking", "split", "boundary", "truncat", "overlap",
        "segment",
    ],
    "prompt_context_ignored": [
        "prompt", "context", "template", "instruct", "reference",
        "grounding", "ignore",
    ],
}


def score_diagnostic(
    failure_mode: str,
    solution: str | None,
    metrics: Dict,
) -> float:
    """Did the candidate correctly identify the root cause?

    Score 1.0 if their solution text contains keywords matching the
    failure mode, or 0.0 otherwise.
    """
    if not solution:
        return 0.0

    keywords = DIAGNOSTIC_KEYWORDS.get(failure_mode, [])
    solution_lower = solution.lower()

    for keyword in keywords:
        if keyword in solution_lower:
            return 1.0

    return 0.0


# =========================================================================
# Rule 2 — Task Success
# =========================================================================

def score_success(
    solution: str | None,
    telemetry_events: List[Dict],
) -> float:
    """Did the candidate submit a solution and run simulations?

    For MVP, success = candidate submitted a solution AND ran at
    least one simulation. Future versions will validate against the
    simulation's expected output.
    """
    if not solution:
        return 0.0

    # Check if any simulation run occurred
    has_sim_run = any(
        e.get("event_type") == "test_run" for e in telemetry_events
    )

    if has_sim_run and len(solution.strip()) > 5:
        return 1.0

    return 0.5  # Partial credit for submitting without testing


# =========================================================================
# Rule 3 — Debugging Efficiency
# =========================================================================

def score_efficiency(metrics: Dict) -> float:
    """How efficiently did the candidate reach a solution?

    Based on the number of simulation runs — fewer runs indicates
    a more targeted debugging approach.
    """
    runs = metrics.get("simulation_runs", 0)

    if runs == 0:
        return 0.0  # Never tested
    elif runs <= 3:
        return 1.0
    elif runs <= 6:
        return 0.7
    elif runs <= 10:
        return 0.4
    else:
        return 0.2


# =========================================================================
# Rule 4 — Iteration Quality
# =========================================================================

def score_iteration(metrics: Dict) -> float:
    """How systematic was the candidate's debugging process?

    Signals:
    - Inspecting retrieval before editing prompts (systematic)
    - Balanced ratio of edits to runs (not guessing randomly)
    - Using available tools
    """
    score = 0.0
    components = 0

    # Component 1: Inspected before editing (worth 0.4)
    if metrics.get("inspected_before_edit", False):
        score += 0.4
    components += 1

    # Component 2: Edit-to-run ratio (worth 0.3)
    runs = metrics.get("simulation_runs", 0)
    edits = metrics.get("prompt_edits", 0)
    if runs > 0:
        ratio = edits / runs
        if 0.3 <= ratio <= 1.0:
            score += 0.3  # Good: roughly one edit per run
        elif ratio > 0:
            score += 0.15  # Some edits happened
    components += 1

    # Component 3: Used retrieval inspection (worth 0.3)
    if metrics.get("retrieval_inspections", 0) > 0:
        score += 0.3
    components += 1

    return round(min(score, 1.0), 2)
