from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.metrics.collections import ContextEntityRecall

client = AsyncOpenAI()
llm = llm_factory("gpt-4o-mini", client=client)
scorer = ContextEntityRecall(llm=llm)


async def get_retrieval_evaluation_dict(
    reference_answer: str,
    actual_contexts: list[dict[str, str]],
) -> dict:
    try:
        recall = await scorer.ascore(
            reference=reference_answer,
            retrieved_contexts=[a["text"] for a in actual_contexts]
        )

        return {
            "retrieval_context_recall": recall.value,
        }
    except Exception as e:
        return {
            "retrieval_context_recall_error": str(e)
        }
