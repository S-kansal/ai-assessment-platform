from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FailureMode:
    name: str
    description: str

    def apply_retrieval(
        self,
        query: str,
        chunks: list[dict],
        corpus: list[dict],
    ) -> list[dict]:
        return chunks

    def apply_generation(
        self,
        query: str,
        prompt_text: str,
        chunks: list[dict],
        current_answer: str,
        confidence_score: float,
    ) -> tuple[str, float]:
        return current_answer, confidence_score


class IrrelevantRetrievalFailure(FailureMode):
    def __init__(self) -> None:
        super().__init__(
            name="irrelevant_retrieval",
            description="The retriever returns topically unrelated chunks.",
        )

    def apply_retrieval(
        self,
        query: str,
        chunks: list[dict],
        corpus: list[dict],
    ) -> list[dict]:
        unrelated = [chunk for chunk in corpus if chunk not in chunks]
        return unrelated[:2] or chunks


class IncorrectChunkingFailure(FailureMode):
    def __init__(self) -> None:
        super().__init__(
            name="incorrect_chunking",
            description="Critical facts are broken across chunk boundaries.",
        )

    def apply_retrieval(
        self,
        query: str,
        chunks: list[dict],
        corpus: list[dict],
    ) -> list[dict]:
        broken_chunks: list[dict] = []
        for chunk in chunks:
            midpoint = max(len(chunk["content"]) // 2, 1)
            broken_chunks.append(
                {
                    **chunk,
                    "content": f"{chunk['content'][:midpoint].rstrip()} ...",
                    "chunking_warning": True,
                }
            )
        return broken_chunks


class ContextIgnoranceFailure(FailureMode):
    def __init__(self) -> None:
        super().__init__(
            name="context_ignorance",
            description="The prompt structure does not force grounded answers.",
        )

    def apply_generation(
        self,
        query: str,
        prompt_text: str,
        chunks: list[dict],
        current_answer: str,
        confidence_score: float,
    ) -> tuple[str, float]:
        answer = (
            "The system appears confident, but it is answering from generic prior "
            "knowledge instead of the supplied context."
        )
        return answer, max(confidence_score, 0.82)


class LowConfidenceHallucinationFailure(FailureMode):
    def __init__(self) -> None:
        super().__init__(
            name="low_confidence_hallucination",
            description="The model hallucinates when retrieval confidence is low.",
        )

    def apply_generation(
        self,
        query: str,
        prompt_text: str,
        chunks: list[dict],
        current_answer: str,
        confidence_score: float,
    ) -> tuple[str, float]:
        answer = (
            "The policy definitely guarantees free replacements within 90 days "
            "for any issue, with no exceptions."
        )
        return answer, 0.91


FAILURE_MODE_REGISTRY = {
    "irrelevant_retrieval": IrrelevantRetrievalFailure(),
    "incorrect_chunking": IncorrectChunkingFailure(),
    "context_ignorance": ContextIgnoranceFailure(),
    "low_confidence_hallucination": LowConfidenceHallucinationFailure(),
}
