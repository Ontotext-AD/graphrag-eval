from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.metrics.collections import ContextRecall, ContextPrecision

from graphrag_eval.util import compute_f1


client = AsyncOpenAI()
llm = llm_factory("gpt-4o-mini", client=client)
recall_scorer = ContextRecall(llm=llm)
precision_scorer = ContextPrecision(llm=llm)


async def get_retrieval_evaluation_dict(
    question_text: str,
    actual_contexts: list[dict[str, str]],
    reference_contexts: list[dict[str, str]],
) -> dict:
    reference = '\n'.join([c["text"] for c in reference_contexts])
    retrieved_contexts = [c["text"] for c in actual_contexts]
    params = dict(
        user_input=question_text,
        reference=reference,
        retrieved_contexts=retrieved_contexts
    )
    result = {}
    try:
        recall = await recall_scorer.ascore(**params)
        result["retrieval_context_recall"] = recall.value
    except Exception as e:
        result["retrieval_context_recall_error"] = str(e)

    try:
        precision = await precision_scorer.ascore(**params)
        result["retrieval_context_precision"] = precision.value
    except Exception as e:
        result["retrieval_context_precision_error"] = str(e)

    if "retrieval_context_recall" in result \
    and "retrieval_context_precision" in result:
        result["retrieval_context_f1"] = compute_f1(
            result["retrieval_context_recall"], 
            result["retrieval_context_precision"],
        )
    return result
