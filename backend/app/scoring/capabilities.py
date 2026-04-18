CAPABILITY_DIMENSIONS = {
    "rag_debugging_skill": {
        "tasks": {
            "rag_irrelevant_retrieval",
            "rag_chunk_boundary",
            "rag_low_confidence_hallucination",
        },
        "weights": {
            "diagnostic_accuracy": 0.4,
            "solution_success": 0.3,
            "iteration_quality": 0.2,
            "efficiency": 0.1,
        },
    },
    "prompt_engineering_skill": {
        "tasks": {"rag_prompt_grounding"},
        "weights": {
            "diagnostic_accuracy": 0.2,
            "solution_success": 0.4,
            "iteration_quality": 0.3,
            "efficiency": 0.1,
        },
    },
    "systematic_diagnostic_reasoning": {
        "tasks": {
            "rag_irrelevant_retrieval",
            "rag_chunk_boundary",
            "rag_prompt_grounding",
            "rag_low_confidence_hallucination",
        },
        "weights": {
            "diagnostic_accuracy": 0.5,
            "iteration_quality": 0.35,
            "efficiency": 0.15,
        },
    },
    "efficiency_under_ambiguity": {
        "tasks": {
            "rag_irrelevant_retrieval",
            "rag_chunk_boundary",
            "rag_low_confidence_hallucination",
        },
        "weights": {
            "efficiency": 0.7,
            "solution_success": 0.3,
        },
    },
}
