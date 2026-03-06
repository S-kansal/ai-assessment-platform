"""Capability mapping — links tasks to the capability they measure.

Each task targets a specific AI engineering capability. When multiple
tasks measure the same capability, scores are aggregated by the
score_aggregator to produce a single per-capability score.
"""

# ---------------------------------------------------------------------------
# MVP capabilities
# ---------------------------------------------------------------------------

CAPABILITIES = [
    "rag_debugging",
    "prompt_engineering",
    "ai_system_reasoning",
    "ai_pipeline_reliability",
]

# ---------------------------------------------------------------------------
# Task → capability mapping
# ---------------------------------------------------------------------------
# weight: how strongly this task contributes to the capability score.
# A weight of 1.0 means full contribution; <1.0 means partial.

TASK_CAPABILITY_MAP = {
    "rag_debug_01": {
        "capability": "rag_debugging",
        "weight": 1.0,
    },
    "rag_debug_02": {
        "capability": "rag_debugging",
        "weight": 1.0,
    },
    "rag_debug_03": {
        "capability": "prompt_engineering",
        "weight": 0.8,
    },
}


def get_capability_for_task(task_id: str) -> dict | None:
    """Return the capability mapping for a task, or None if unmapped."""
    return TASK_CAPABILITY_MAP.get(task_id)
