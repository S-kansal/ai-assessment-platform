from __future__ import annotations

from math import isfinite


def clamp(value: float) -> float:
    if not isfinite(value):
        return 0.0
    return round(max(0.0, min(1.0, value)), 4)


def diagnostic_accuracy(submitted_root_cause: str, expected_failure_modes: list[str]) -> float:
    if not submitted_root_cause.strip():
        return 0.0
    text = submitted_root_cause.lower()
    matches = sum(
        1
        for mode in expected_failure_modes
        if mode in text or mode.replace("_", " ") in text
    )
    return clamp(matches / max(len(expected_failure_modes), 1))


def solution_success(successful_final_run: bool) -> float:
    return 1.0 if successful_final_run else 0.0


def efficiency(
    elapsed_minutes: float,
    simulation_runs: int,
    target_minutes: int,
    target_simulation_runs: int,
) -> float:
    if simulation_runs == 0:
        return 0.0
    time_component = 1.0 - min(elapsed_minutes / max(target_minutes, 1), 1.0)
    run_component = 1.0 - min(
        max(simulation_runs - target_simulation_runs, 0) / max(target_simulation_runs, 1),
        1.0,
    )
    return clamp((time_component * 0.5) + (run_component * 0.5))


def iteration_quality(
    successful_runs: int,
    simulation_runs: int,
    prompt_edits: int,
    log_inspections: int,
) -> float:
    if simulation_runs == 0:
        return 0.0
    improvement_ratio = successful_runs / simulation_runs
    edit_discipline = 1.0 if prompt_edits <= simulation_runs + 2 else 0.5
    evidence_usage = 1.0 if log_inspections > 0 else 0.4
    return clamp((improvement_ratio * 0.5) + (edit_discipline * 0.25) + (evidence_usage * 0.25))
