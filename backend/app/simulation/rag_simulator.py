"""Deterministic RAG pipeline simulator.

Simulates retrieval, prompt assembly, and generation stages of a RAG system.
All outputs are deterministic — the same inputs and state always produce the
same outputs, enabling fair and comparable candidate assessment.
"""

from typing import Dict, List

from app.simulation.rag_documents import DOCUMENTS
from app.simulation.rag_state import RAGState
from app.simulation.rag_failures import FAILURE_MODES


# =========================================================================
# Retrieval stage
# =========================================================================

def simulate_retrieval(query: str, state: RAGState) -> List[Dict]:
    """Simulate the embedding-search + chunk-retrieval stage.

    Returns a list of document chunks based on the active failure mode.
    """
    query_lower = query.lower()

    if state.failure_mode == "irrelevant_retrieval":
        # Return documents that do NOT match the query topic
        if "refund" in query_lower or "return" in query_lower:
            return [DOCUMENTS[1], DOCUMENTS[4]]  # Shipping + Account (wrong)
        elif "shipping" in query_lower:
            return [DOCUMENTS[0], DOCUMENTS[3]]  # Refund + Warranty (wrong)
        else:
            return [DOCUMENTS[1], DOCUMENTS[4]]  # Generic wrong docs

    elif state.failure_mode == "incorrect_chunking":
        # Return a truncated version of the correct document (bad chunking)
        correct_doc = _find_relevant_document(query_lower)
        if correct_doc:
            truncated = {
                "id": correct_doc["id"],
                "title": correct_doc["title"],
                "content": correct_doc["content"][:40] + "...",  # Cut off
            }
            return [truncated]
        return [DOCUMENTS[0]]

    else:
        # No retrieval failure — return the correct document
        correct_doc = _find_relevant_document(query_lower)
        if correct_doc:
            return [correct_doc]
        return [DOCUMENTS[0]]


def _find_relevant_document(query_lower: str) -> dict | None:
    """Simple keyword matching to find the relevant document."""
    keyword_map = {
        "refund": "doc-001",
        "ship": "doc-002",
        "return": "doc-003",
        "warranty": "doc-004",
        "account": "doc-005",
        "password": "doc-005",
    }
    for keyword, doc_id in keyword_map.items():
        if keyword in query_lower:
            for doc in DOCUMENTS:
                if doc["id"] == doc_id:
                    return doc
    return None


# =========================================================================
# Prompt assembly
# =========================================================================

def assemble_prompt(
    query: str,
    retrieved_chunks: List[Dict],
    prompt_template: str,
) -> str:
    """Assemble the final prompt from the template, context, and query."""
    context = "\n\n".join(
        f"[{chunk['title']}]: {chunk['content']}"
        for chunk in retrieved_chunks
    )
    return (
        f"{prompt_template}\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}"
    )


# =========================================================================
# Generation stage
# =========================================================================

def simulate_generation(
    query: str,
    retrieved_chunks: List[Dict],
    assembled_prompt: str,
    state: RAGState,
) -> str:
    """Simulate deterministic LLM generation based on state and context.

    The generated answer depends on the failure mode and whether the
    correct context was retrieved.
    """
    query_lower = query.lower()

    # -- Failure: prompt ignores context --------------------------------
    if state.failure_mode == "prompt_context_ignored":
        return (
            "I'm not sure about the specific policy. Generally, most "
            "companies offer some form of refund or return option. Please "
            "check the company website for details."
        )

    # -- Failure: irrelevant retrieval ----------------------------------
    if state.failure_mode == "irrelevant_retrieval":
        # Model answers based on wrong context
        if "refund" in query_lower:
            return (
                "Orders ship within 2 business days. Express shipping is "
                "available for an additional fee."
            )
        elif "shipping" in query_lower:
            return (
                "Customers may request a full refund within 30 days of "
                "purchase."
            )
        else:
            return "I could not find relevant information for your question."

    # -- Failure: incorrect chunking ------------------------------------
    if state.failure_mode == "incorrect_chunking":
        # Model answers from truncated context
        if "refund" in query_lower:
            return "Customers may request a full refund within"
        elif "return" in query_lower:
            return "Items may be returned if they are"
        else:
            return "The information appears incomplete."

    # -- No failure (correct behaviour) ---------------------------------
    correct_doc = _find_relevant_document(query_lower)
    if correct_doc:
        return correct_doc["content"]

    return "I don't have enough information to answer that question."


# =========================================================================
# Debug logs
# =========================================================================

def generate_debug_logs(
    query: str,
    state: RAGState,
    retrieved_chunks: List[Dict],
) -> List[str]:
    """Generate observability-style debug logs for the simulation run."""
    failure_info = FAILURE_MODES.get(state.failure_mode, {})
    logs = [
        f"[RETRIEVAL] Embedding search executed for query: \"{query}\"",
        f"[RETRIEVAL] Top-{state.retrieval_k} retrieval requested "
        f"(chunk_size={state.chunk_size})",
        f"[RETRIEVAL] {len(retrieved_chunks)} document(s) retrieved: "
        f"{[c['id'] for c in retrieved_chunks]}",
        f"[PROMPT] Prompt constructed using template "
        f"({len(state.prompt_template)} chars)",
        f"[GENERATION] Generation step completed",
    ]
    if failure_info:
        logs.append(
            f"[DEBUG] Active failure mode: {state.failure_mode} — "
            f"{failure_info.get('symptom', 'unknown symptom')}"
        )
    return logs


# =========================================================================
# Full pipeline
# =========================================================================

def run_rag_pipeline(
    query: str,
    prompt_template: str,
    state: RAGState | None = None,
) -> Dict:
    """Execute the full deterministic RAG pipeline.

    Pipeline: query → retrieval → prompt assembly → generation → output

    Returns a dictionary containing retrieved chunks, generated answer,
    and debug logs.
    """
    if state is None:
        state = RAGState()

    # Override prompt template if provided
    if prompt_template:
        state.prompt_template = prompt_template

    # Stage 1: Retrieval
    retrieved_chunks = simulate_retrieval(query, state)

    # Stage 2: Prompt assembly
    assembled_prompt = assemble_prompt(query, retrieved_chunks, state.prompt_template)

    # Stage 3: Generation
    generated_answer = simulate_generation(
        query, retrieved_chunks, assembled_prompt, state
    )

    # Stage 4: Debug logs
    debug_logs = generate_debug_logs(query, state, retrieved_chunks)

    return {
        "retrieved_chunks": retrieved_chunks,
        "generated_answer": generated_answer,
        "assembled_prompt": assembled_prompt,
        "debug_logs": debug_logs,
        "simulation_state": state.to_dict(),
    }
