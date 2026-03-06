"""MVP task library — defines all available assessment tasks.

Each task maps to a simulation environment and a specific failure mode
that the candidate must diagnose. The Task Engine loads definitions from
this library when starting a task run.
"""

TASK_LIBRARY = {
    "rag_debug_01": {
        "name": "RAG Retrieval Failure",
        "description": (
            "A customer support chatbot retrieves irrelevant documents "
            "when answering user questions, even though the correct "
            "document exists in the knowledge base. Diagnose and fix "
            "the retrieval issue."
        ),
        "capability_target": "rag_debugging",
        "task_type": "rag_debugging",
        "simulation_type": "rag",
        "failure_mode": "irrelevant_retrieval",
    },
    "rag_debug_02": {
        "name": "RAG Chunking Failure",
        "description": (
            "A document retrieval pipeline returns only partial "
            "information because documents are chunked at bad boundaries. "
            "The candidate must identify the chunking problem."
        ),
        "capability_target": "rag_debugging",
        "task_type": "rag_debugging",
        "simulation_type": "rag",
        "failure_mode": "incorrect_chunking",
    },
    "rag_debug_03": {
        "name": "Prompt Context Ignored",
        "description": (
            "The model ignores retrieved context documents and generates "
            "an answer from its own knowledge, which is incorrect. The "
            "candidate must fix the prompt template to reference context."
        ),
        "capability_target": "prompt_engineering",
        "task_type": "prompt_stability",
        "simulation_type": "rag",
        "failure_mode": "prompt_context_ignored",
    },
}
