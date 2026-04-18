from __future__ import annotations

import hashlib
from dataclasses import dataclass

from app.core.config import settings
from app.simulation.failure_modes import FAILURE_MODE_REGISTRY
from app.simulation.scenarios import SCENARIOS


GROUNDING_KEYWORDS = ("only use the context", "ground", "do not know", "insufficient")


@dataclass
class SimulationOutput:
    retrieved_chunks: list[dict]
    debug_logs: list[str]
    response_text: str
    output_quality: dict
    confidence_score: float
    seed: int


def _keyword_score(query_text: str, content: str) -> int:
    tokens = {token.strip("?.!,").lower() for token in query_text.split() if token.strip()}
    return sum(1 for token in tokens if token and token in content.lower())


def _seed_for(prompt_text: str, query_text: str, scenario_key: str) -> int:
    digest = hashlib.sha256(
        f"{settings.simulation_seed}:{scenario_key}:{prompt_text}:{query_text}".encode("utf-8")
    ).hexdigest()
    return int(digest[:8], 16)


def _retrieve_chunks(query_text: str, documents: list[dict]) -> tuple[list[dict], float]:
    scored = sorted(
        (
            {**document, "score": _keyword_score(query_text, document["content"])}
            for document in documents
        ),
        key=lambda item: (-item["score"], item["id"]),
    )
    top_chunks = scored[:2]
    confidence = min(1.0, max(sum(item["score"] for item in top_chunks) / 10.0, 0.1))
    return top_chunks, round(confidence, 2)


def _grounded_answer(prompt_text: str, chunks: list[dict], confidence_score: float) -> str:
    prompt_lower = prompt_text.lower()
    if confidence_score < 0.35 and any(keyword in prompt_lower for keyword in GROUNDING_KEYWORDS):
        return "I do not have enough grounded context to answer confidently."
    if not chunks:
        return "I do not have enough grounded context to answer confidently."
    return chunks[0]["content"]


def run_simulation(
    scenario_key: str,
    failure_modes: list[str],
    prompt_text: str,
    query_text: str,
) -> SimulationOutput:
    scenario = SCENARIOS[scenario_key]
    seed = _seed_for(prompt_text, query_text, scenario_key)
    retrieved_chunks, confidence_score = _retrieve_chunks(query_text, scenario["documents"])

    debug_logs = [
        f"[PIPELINE] Scenario: {scenario_key}",
        f"[QUERY] {query_text}",
        f"[RETRIEVAL] Retrieved {len(retrieved_chunks)} chunks before failures",
        f"[CONFIDENCE] Retrieval confidence={confidence_score}",
    ]

    for mode_name in failure_modes:
        failure_mode = FAILURE_MODE_REGISTRY[mode_name]
        retrieved_chunks = failure_mode.apply_retrieval(
            query_text,
            retrieved_chunks,
            scenario["documents"],
        )
        debug_logs.append(f"[FAILURE] Applied retrieval transformation for {mode_name}")

    answer = _grounded_answer(prompt_text, retrieved_chunks, confidence_score)
    for mode_name in failure_modes:
        failure_mode = FAILURE_MODE_REGISTRY[mode_name]
        answer, confidence_score = failure_mode.apply_generation(
            query_text,
            prompt_text,
            retrieved_chunks,
            answer,
            confidence_score,
        )
        debug_logs.append(f"[FAILURE] Applied generation transformation for {mode_name}")

    if "context_ignorance" not in failure_modes and any(
        keyword in prompt_text.lower() for keyword in GROUNDING_KEYWORDS
    ):
        debug_logs.append("[PROMPT] Grounding instruction detected in prompt")

    output_quality = {
        "is_grounded": (
            "context_ignorance" not in failure_modes
            and (
                "grounded context" in answer.lower()
                or answer in [chunk["content"] for chunk in retrieved_chunks]
            )
        ),
        "active_failure_modes": failure_modes,
        "retrieval_confidence": confidence_score,
    }
    return SimulationOutput(
        retrieved_chunks=retrieved_chunks,
        debug_logs=debug_logs,
        response_text=answer,
        output_quality=output_quality,
        confidence_score=round(confidence_score, 2),
        seed=seed,
    )
