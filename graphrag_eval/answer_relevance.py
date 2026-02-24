from ragas.embeddings.base import BaseRagasEmbedding
from ragas.llms.base import InstructorBaseRagasLLM
from ragas.metrics.collections import AnswerRelevancy


class Evaluator:
    def __init__(self, ragas_llm: InstructorBaseRagasLLM, ragas_embedder: BaseRagasEmbedding):
        self.ragas_llm = ragas_llm
        self.ragas_embedder = ragas_embedder

    async def get_relevance_dict(
        self,
        question_text: str,
        actual_answer: str,
    ) -> dict:
        scorer = AnswerRelevancy(llm=self.ragas_llm, embeddings=self.ragas_embedder)
        try:
            result = await scorer.ascore(
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
