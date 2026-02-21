from ragas.metrics.collections import AnswerRelevancy


async def get_relevance_dict(
    question_text: str,
    actual_answer: str,
    ragas_llm,
    ragas_embeddings,
) -> dict:
    scorer = AnswerRelevancy(llm=ragas_llm, embeddings=ragas_embeddings)
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
