TASK_DEFINITIONS = [
    {
        "id": "rag_irrelevant_retrieval",
        "title": "RAG Retrieval Drift",
        "task_type": "rag_debugging",
        "failure_modes": ["irrelevant_retrieval"],
        "expected_diagnostic_path": [
            "run_query",
            "inspect_logs",
            "inspect_retrieved_chunks",
            "identify_irrelevant_retrieval",
        ],
        "success_criteria": {
            "required_phrases": ["30-day return window"],
            "must_use_grounding": True,
        },
        "rubric": {
            "target_simulation_runs": 3,
            "target_minutes": 12,
        },
        "scenario_key": "returns_policy_retrieval",
    },
    {
        "id": "rag_chunk_boundary",
        "title": "Chunk Boundary Failure",
        "task_type": "rag_debugging",
        "failure_modes": ["incorrect_chunking"],
        "expected_diagnostic_path": [
            "run_query",
            "inspect_logs",
            "inspect_retrieved_chunks",
            "identify_chunk_boundary_failure",
        ],
        "success_criteria": {
            "required_phrases": ["5-7 business days"],
            "must_use_grounding": True,
        },
        "rubric": {
            "target_simulation_runs": 4,
            "target_minutes": 15,
        },
        "scenario_key": "refund_processing_chunking",
    },
    {
        "id": "rag_prompt_grounding",
        "title": "Prompt Grounding Failure",
        "task_type": "prompt_engineering",
        "failure_modes": ["context_ignorance"],
        "expected_diagnostic_path": [
            "run_query",
            "inspect_logs",
            "identify_prompt_grounding_gap",
            "rewrite_prompt",
        ],
        "success_criteria": {
            "required_phrases": ["I do not know"],
            "must_use_grounding": True,
        },
        "rubric": {
            "target_simulation_runs": 3,
            "target_minutes": 10,
        },
        "scenario_key": "grounding_prompt_rewrite",
    },
    {
        "id": "rag_low_confidence_hallucination",
        "title": "Low-Confidence Hallucination",
        "task_type": "rag_debugging",
        "failure_modes": ["low_confidence_hallucination"],
        "expected_diagnostic_path": [
            "run_query",
            "inspect_logs",
            "inspect_retrieved_chunks",
            "identify_low_confidence_hallucination",
        ],
        "success_criteria": {
            "required_phrases": ["I do not have enough grounded context"],
            "must_use_grounding": True,
        },
        "rubric": {
            "target_simulation_runs": 4,
            "target_minutes": 12,
        },
        "scenario_key": "abstain_when_retrieval_is_weak",
    },
]


def list_task_definitions() -> list[dict]:
    return [definition.copy() for definition in TASK_DEFINITIONS]


def get_task_definition(task_id: str) -> dict | None:
    for definition in TASK_DEFINITIONS:
        if definition["id"] == task_id:
            return definition.copy()
    return None
