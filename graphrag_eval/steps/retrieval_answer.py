from ragas.llms.base import InstructorBaseRagasLLM
from ragas.metrics.collections import ContextRecall, ContextPrecision

from graphrag_eval.util import compute_f1


class Evaluator:
    def __init__(self, ragas_llm: InstructorBaseRagasLLM):
        self.ragas_llm = ragas_llm

    async def get_retrieval_evaluation_dict(
        self,
        question_text: str,
        reference_answer: str,
        actual_contexts: list[dict[str, str]],
    ) -> dict:
        retrieved_contexts = [a["text"] for a in actual_contexts]
        params = dict(
            user_input=question_text,
            reference=reference_answer,
            retrieved_contexts=retrieved_contexts
        )
        result = {}
        recall_scorer = ContextRecall(llm=self.ragas_llm)
        precision_scorer = ContextPrecision(llm=self.ragas_llm)
        try:
            recall = await recall_scorer.ascore(**params)
            result["retrieval_answer_recall"] = recall.value
        except Exception as e:
            result["retrieval_answer_recall_error"] = str(e)
    
        try:
            precision = await precision_scorer.ascore(**params)
            result["retrieval_answer_precision"] = precision.value
        except Exception as e:
            result["retrieval_answer_precision_error"] = str(e)
    
        if "retrieval_answer_recall" in result \
        and "retrieval_answer_precision" in result:
            result["retrieval_answer_f1"] = compute_f1(
                result["retrieval_answer_recall"], 
                result["retrieval_answer_precision"],
            )
        return result
