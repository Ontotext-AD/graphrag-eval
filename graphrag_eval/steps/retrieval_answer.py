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
    reference_answer: str,
    actual_contexts: list[dict[str, str]],
) -> dict:
    result = {}

    try:
        recall = await recall_scorer.ascore(
            user_input=question_text,
            reference=reference_answer,
            retrieved_contexts=[a["text"] for a in actual_contexts]
        )
        result.update({"retrieval_answer_recall": recall.value})
    except Exception as e:
        result.update({
            "retrieval_answer_recall_error": str(e)
        })

    try:
        precision = await precision_scorer.ascore(
            user_input=question_text,
            reference=reference_answer,
            retrieved_contexts=[a["text"] for a in actual_contexts]
        )
        result.update({"retrieval_answer_precision": precision.value})
    except Exception as e:
        result.update({
            "retrieval_answer_precision_error": str(e)
        })

    if "retrieval_answer_recall" in result and "retrieval_answer_precision" in result:
        result.update({
            "retrieval_answer_f1": compute_f1(result["retrieval_answer_recall"], result["retrieval_answer_precision"])
        })
    return result
