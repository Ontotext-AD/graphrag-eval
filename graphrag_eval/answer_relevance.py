from openai import AsyncOpenAI
from ragas.embeddings.base import embedding_factory
from ragas.llms import llm_factory
from ragas.metrics.collections import AnswerRelevancy

client = AsyncOpenAI()
llm = llm_factory("gpt-4o-mini", client=client)
embeddings = embedding_factory("openai", model="text-embedding-3-small", client=client)
scorer = AnswerRelevancy(llm=llm, embeddings=embeddings)


async def get_relevance_dict(
    question_text: str,
    actual_answer: str,
) -> dict:
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
