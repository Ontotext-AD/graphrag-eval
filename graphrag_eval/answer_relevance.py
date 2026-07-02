from __future__ import annotations

from typing import Any, Self, TYPE_CHECKING

from pydantic import BaseModel, Field

from .evaluator import Evaluator

if TYPE_CHECKING:
    from ragas.llms.base import InstructorBaseRagasLLM
    from ragas.embeddings.base import BaseRagasEmbeddings, BaseRagasEmbedding


class AnswerRelevanceConfig(BaseModel):
    enabled: bool = Field(default=True)


class AnswerRelevanceEvaluator:
    def __init__(
        self,
        ragas_llm: InstructorBaseRagasLLM,
        ragas_embedder: BaseRagasEmbeddings | BaseRagasEmbedding
    ):
        from ragas.metrics.collections import AnswerRelevancy
        self.scorer = AnswerRelevancy(llm=ragas_llm, embeddings=ragas_embedder)

    @classmethod
    def from_config(
        cls,
        ragas_llm: InstructorBaseRagasLLM | None,
        ragas_embedder: BaseRagasEmbeddings | BaseRagasEmbedding | None,
        config: AnswerRelevanceConfig | None
    ) -> Self | None:
        if ragas_llm is None or ragas_embedder is None:
            return None
        if config is None or not config.enabled:
            return None
        return cls(ragas_llm=ragas_llm, ragas_embedder=ragas_embedder)

    async def evaluate(
        self,
        reference: dict[str, Any],
        actual: dict[str, Any]
    ) -> dict[str, Any]:
        if "actual_answer" not in actual:
            return {}
        try:
            result = await self.scorer.ascore(
                user_input=reference["question_text"],
                response=actual["actual_answer"]
            )
            return {
                "answer_relevance": result.value
            }
        except Exception as e:
            return {
                "answer_relevance_error": str(e)
            }


_: Evaluator = AnswerRelevanceEvaluator
