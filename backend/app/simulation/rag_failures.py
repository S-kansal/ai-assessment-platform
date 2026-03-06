"""Deterministic failure modes for the RAG simulation.

Each failure mode alters the simulator's retrieval and generation behaviour in
a predictable way so that candidate performance is measurable and repeatable.
"""

FAILURE_MODES = {
    "incorrect_chunking": {
        "description": "Documents are chunked at incorrect boundaries, "
                       "splitting critical information across chunks.",
        "symptom": "Relevant information is missing from retrieved chunks — "
                   "only partial context is returned.",
        "affected_stage": "retrieval",
    },
    "irrelevant_retrieval": {
        "description": "Embedding similarity matching fails, causing the "
                       "retriever to return documents unrelated to the query.",
        "symptom": "Wrong documents are retrieved despite the correct "
                   "document existing in the knowledge base.",
        "affected_stage": "retrieval",
    },
    "prompt_context_ignored": {
        "description": "The prompt template does not properly instruct the "
                       "model to reference the retrieved context.",
        "symptom": "The model ignores the retrieved documents and generates "
                   "an answer from its own knowledge, which is incorrect.",
        "affected_stage": "generation",
    },
}


# ---------------------------------------------------------------------------
# Task-to-simulation mapping
# ---------------------------------------------------------------------------
# Maps task IDs to the failure mode that should be activated for that task.
# The task engine will use this mapping to initialise the simulation.

TASK_SIMULATION_MAP = {
    "rag_debug_01": {
        "simulation_type": "rag_pipeline",
        "failure_mode": "irrelevant_retrieval",
        "name": "RAG Retrieval Failure",
        "description": (
            "A customer support chatbot answers incorrectly even though the "
            "correct document exists in the knowledge base. The candidate "
            "must diagnose the retrieval issue."
        ),
    },
    "rag_debug_02": {
        "simulation_type": "rag_pipeline",
        "failure_mode": "incorrect_chunking",
        "name": "RAG Chunking Failure",
        "description": (
            "The retriever returns partial information because documents are "
            "chunked at bad boundaries. The candidate must identify and fix "
            "the chunking problem."
        ),
    },
    "rag_debug_03": {
        "simulation_type": "rag_pipeline",
        "failure_mode": "prompt_context_ignored",
        "name": "RAG Prompt Context Issue",
        "description": (
            "The model ignores retrieved context and hallucinates an answer. "
            "The candidate must fix the prompt template to reference context."
        ),
    },
}
