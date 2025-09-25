from langevals_ragas.context_precision import (
    RagasContextPrecisionEntry,
    RagasContextPrecisionEvaluator,
)
from langevals_ragas.context_recall import (
    RagasContextRecallEntry,
    RagasContextRecallEvaluator,
)

from graphrag_eval.util import get_f1_dict


def _evaluate(
    entry: RagasContextRecallEntry | RagasContextPrecisionEntry,
    evauator: RagasContextRecallEvaluator | RagasContextPrecisionEvaluator,
    metric: str
) -> dict:
    try:
        result = evauator.evaluate(entry)
        if result.status == "processed":
            result_dict = {
                f"retrieval_context_{metric}": result.score,                
            }
            if result.details:
                result_dict[f"retrieval_context_{metric}_reason"] = result.details
            if result.cost is not None:
                result_dict[f"retrieval_context_{metric}_cost"] = result.cost.amount
            return result_dict
        else:
            return {
                f"retrieval_context_{metric}_error": result.details,
            }
    except Exception as e:
        return {
            f"retrieval_context_{metric}_error": str(e),
        }


def get_retrieval_evaluation_dict(
    reference_contexts: list[dict[str, str]],
    actual_contexts: list[dict[str, str]],
    model_name : str = "openai/gpt-4o-mini",
    max_tokens : int = 65_536
) -> dict:
    settings_dict = {
        "model": model_name,
        "max_tokens": max_tokens
    }
    entry = RagasContextRecallEntry(
        expected_contexts=[a["text"] for a in reference_contexts],
        contexts=[a["text"] for a in actual_contexts]
    )
    result = {}
    evaluator = RagasContextRecallEvaluator(settings=settings_dict)
    result.update(_evaluate(entry, evaluator, "recall"))
    evaluator = RagasContextPrecisionEvaluator(settings=settings_dict)
    result.update(_evaluate(entry, evaluator, "precision"))
    result.update(get_f1_dict(result, "retrieval_context"))
    return result
