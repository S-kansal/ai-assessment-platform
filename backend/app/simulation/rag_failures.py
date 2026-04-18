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
