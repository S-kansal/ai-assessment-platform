SUCCESS_CHECKS = {
    "rag_irrelevant_retrieval": ["30-day return window"],
    "rag_chunk_boundary": ["5-7 business days"],
    "rag_prompt_grounding": ["i do not know"],
    "rag_low_confidence_hallucination": ["i do not have enough grounded context"],
}


def canonical_task_id(task_id: str) -> str:
    return task_id.split(":", 1)[-1]


def check_success(task_id: str, final_response_text: str) -> bool:
    checks = SUCCESS_CHECKS.get(canonical_task_id(task_id), [])
    response = final_response_text.lower()
    return all(required_phrase.lower() in response for required_phrase in checks)
