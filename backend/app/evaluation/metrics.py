"""Telemetry metrics extractor.

Converts raw telemetry events into structured behavioural metrics that the
evaluation rules consume. Metrics are computed from event counts, ordering,
and timestamps.
"""

from typing import Dict, List


def extract_metrics(events: List[Dict]) -> Dict:
    """Extract behavioural metrics from a list of telemetry events.

    Args:
        events: List of telemetry event dicts, each with at least
                'event_type', 'timestamp', and 'payload_json'.

    Returns:
        Dictionary of computed metrics.
    """
    # --- Count events by type ---
    simulation_runs = 0
    prompt_edits = 0
    retrieval_inspections = 0
    query_changes = 0
    tool_usages = 0
    solution_submits = 0

    timestamps = []

    for event in events:
        etype = event.get("event_type", "")
        ts = event.get("timestamp")
        if ts:
            timestamps.append(ts)

        if etype == "test_run":
            simulation_runs += 1
        elif etype == "prompt_edit":
            prompt_edits += 1
        elif etype == "retrieval_inspection":
            retrieval_inspections += 1
        elif etype == "query_change":
            query_changes += 1
        elif etype == "tool_usage":
            tool_usages += 1
        elif etype == "solution_submit":
            solution_submits += 1

    # --- Time to solution (seconds) ---
    time_to_solution = 0.0
    if len(timestamps) >= 2:
        sorted_ts = sorted(timestamps)
        delta = sorted_ts[-1] - sorted_ts[0]
        time_to_solution = delta.total_seconds()

    # --- Check debugging order (inspected before editing?) ---
    inspected_before_edit = _check_inspect_before_edit(events)

    return {
        "simulation_runs": simulation_runs,
        "prompt_edits": prompt_edits,
        "retrieval_inspections": retrieval_inspections,
        "query_changes": query_changes,
        "tool_usages": tool_usages,
        "solution_submits": solution_submits,
        "time_to_solution": time_to_solution,
        "total_events": len(events),
        "inspected_before_edit": inspected_before_edit,
    }


def _check_inspect_before_edit(events: List[Dict]) -> bool:
    """Check if the candidate inspected retrieval results before editing prompts.

    This is a signal of systematic debugging: diagnosing before fixing.
    """
    first_inspection_idx = None
    first_edit_idx = None

    for i, event in enumerate(events):
        etype = event.get("event_type", "")
        if etype == "retrieval_inspection" and first_inspection_idx is None:
            first_inspection_idx = i
        if etype == "prompt_edit" and first_edit_idx is None:
            first_edit_idx = i

    if first_inspection_idx is not None and first_edit_idx is not None:
        return first_inspection_idx < first_edit_idx

    # If only inspection happened (no edit), considered good practice
    if first_inspection_idx is not None and first_edit_idx is None:
        return True

    return False
