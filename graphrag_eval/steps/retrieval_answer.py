from langevals_ragas.response_context_recall import (
    RagasResponseContextRecallEntry,
    RagasResponseContextRecallEvaluator,
)
from langevals_ragas.response_context_precision import (
    RagasResponseContextPrecisionEntry,
    RagasResponseContextPrecisionEvaluator,
)

from graphrag_eval import llm
from graphrag_eval.util import get_f1_dict


def _evaluate(
    evaluator: RagasResponseContextRecallEvaluator | RagasResponseContextPrecisionEvaluator,
    entry: RagasResponseContextRecallEntry | RagasResponseContextPrecisionEntry,
    metric: str
) -> dict[str, float | str]:
    try:
        le_result = evaluator.evaluate(entry)
        if le_result.status == "processed":
            result = {
                f"retrieval_answer_{metric}": le_result.score,
            }
            if le_result.cost:
                result[f"retrieval_answer_{metric}_cost"] = le_result.cost.amount
            if le_result.details:
                result[f"retrieval_answer_{metric}_reason"] = le_result.details
            return result
        else:
            return {
                f"retrieval_answer_{metric}_error": le_result.details
            }
    except Exception as e:
        return {
            f"retrieval_answer_{metric}_error": str(e)
        }


def get_retrieval_evaluation_dict(
    llm_config: llm.Config,
    question_text: str,
    actual_contexts: list[dict[str, str]],
    reference_answer: str | None = None,
    actual_answer: str | None = None,
) -> dict:
    if not reference_answer and not actual_answer:
        return {}
    settings_dict = {
        "model": llm_config.name,
        "max_tokens": llm_config.max_tokens
    }
    entry = RagasResponseContextPrecisionEntry(
        input=question_text,
        expected_output=reference_answer,
        output=actual_answer,
        contexts=[a["text"] for a in actual_contexts]
    )
    result = {}
    evaluator = RagasResponseContextRecallEvaluator(settings=settings_dict)
    result.update(_evaluate(evaluator, entry, "recall"))
    evaluator = RagasResponseContextPrecisionEvaluator(settings=settings_dict)
    result.update(_evaluate(evaluator, entry, "precision"))
    result.update(get_f1_dict(result, "retrieval_answer"))
    return result
