from langevals_ragas.context_precision import (
    RagasContextPrecisionEntry,
    RagasContextPrecisionEvaluator,
)
from langevals_ragas.context_recall import (
    RagasContextRecallEntry,
    RagasContextRecallEvaluator,
)

from graphrag_eval import llm
from graphrag_eval.util import get_f1_dict


def _evaluate(
    entry: RagasContextRecallEntry | RagasContextPrecisionEntry,
    evaluator: RagasContextRecallEvaluator | RagasContextPrecisionEvaluator,
    metric: str
) -> dict:
    try:
        result = evaluator.evaluate(entry)
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
    llm_config: llm.Config
) -> dict:
    settings_dict = {
        "model": llm_config.name,
        "max_tokens": llm_config.max_tokens
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
