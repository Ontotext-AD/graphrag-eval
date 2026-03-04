from ragas.embeddings.base import BaseRagasEmbedding
from ragas.llms.base import InstructorBaseRagasLLM
from ragas.metrics.collections import AnswerRelevancy


class Evaluator:
    def __init__(self, ragas_llm: InstructorBaseRagasLLM, ragas_embedder: BaseRagasEmbedding):
        self.scorer = AnswerRelevancy(llm=ragas_llm, embeddings=ragas_embedder)

    async def get_relevance_dict(
        self,
        question_text: str,
        actual_answer: str,
    ) -> dict:
        try:
            result = await self.scorer.ascore(
                user_input=question_text,
                response=actual_answer
            )
            return {
                "answer_relevance": result.value
            }
        except Exception as e:
            return {
                "answer_relevance_error": str(e)
            }
