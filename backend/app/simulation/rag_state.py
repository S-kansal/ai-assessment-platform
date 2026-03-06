"""Simulation state for a RAG pipeline.

RAGState represents the internal configuration of the simulated AI system.
Candidates do not modify this directly — their actions (prompt edits,
retrieval parameter changes) are translated into state mutations by the
simulation engine.
"""


class RAGState:
    """Configuration state for a single RAG simulation instance."""

    def __init__(
        self,
        chunk_size: int = 500,
        retrieval_k: int = 3,
        prompt_template: str = "Use the context to answer.",
        failure_mode: str = "irrelevant_retrieval",
    ):
        self.chunk_size = chunk_size
        self.retrieval_k = retrieval_k
        self.prompt_template = prompt_template
        self.failure_mode = failure_mode

    def to_dict(self) -> dict:
        """Serialise state for logging and debugging."""
        return {
            "chunk_size": self.chunk_size,
            "retrieval_k": self.retrieval_k,
            "prompt_template": self.prompt_template,
            "failure_mode": self.failure_mode,
        }
