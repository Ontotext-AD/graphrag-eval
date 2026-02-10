from langevals_ragas.response_relevancy import (
    RagasResponseRelevancyEvaluator,
    RagasResponseRelevancyEntry
)

from graphrag_eval import llm


def get_relevance_dict(
    question_text: str,
    actual_answer: str,
    llm_config: llm.Config,
) -> dict:
    settings_dict = {
        'model': llm_config.name,
        'max_tokens': llm_config.max_tokens
    }
    entry = RagasResponseRelevancyEntry(
        input=question_text,
        output=actual_answer
    )
    evaluator = RagasResponseRelevancyEvaluator(settings=settings_dict)
    try:
        result = evaluator.evaluate(entry)
        if result.status == "processed":
            return {
                "answer_relevance": result.score,
                "answer_relevance_cost": result.cost.amount,
                "answer_relevance_reason": result.details,
            }
        else:
            return {
                "answer_relevance_error": result.details
            }
    except Exception as e:
        return {
            "answer_relevance_error": str(e),
        }
