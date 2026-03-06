"""Capability score aggregator.

When multiple tasks measure the same capability, this module computes a
weighted average of the individual task scores to produce a single
per-capability score.
"""

from typing import Dict, List

from app.scoring.capability_map import get_capability_for_task


def aggregate_capability_scores(
    task_scores: List[Dict],
) -> Dict[str, float]:
    """Aggregate task-level scores into capability-level scores.

    Args:
        task_scores: List of dicts, each containing:
            - task_id: str
            - task_score: float (0–100)

    Returns:
        Dict mapping capability name → aggregated score (0–100).
    """
    # Group scores by capability
    capability_buckets: Dict[str, List[Dict]] = {}

    for entry in task_scores:
        task_id = entry["task_id"]
        mapping = get_capability_for_task(task_id)

        if mapping is None:
            continue  # Unmapped task — skip

        capability = mapping["capability"]
        weight = mapping["weight"]

        if capability not in capability_buckets:
            capability_buckets[capability] = []

        capability_buckets[capability].append({
            "score": entry["task_score"],
            "weight": weight,
        })

    # Compute weighted average per capability
    capability_scores: Dict[str, Dict] = {}

    for capability, entries in capability_buckets.items():
        total_weight = sum(e["weight"] for e in entries)
        if total_weight == 0:
            capability_scores[capability] = {"score": 0.0, "sample_size": 0}
            continue

        weighted_sum = sum(e["score"] * e["weight"] for e in entries)
        capability_scores[capability] = {
            "score": round(weighted_sum / total_weight, 1),
            "sample_size": len(entries),
        }

    return capability_scores
