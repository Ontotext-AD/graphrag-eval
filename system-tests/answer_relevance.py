import pytest

from graphrag_eval.answer_relevance import (
    get_relevance_dict
)


@pytest.mark.asyncio
async def test_answer_relevance():
    result = await get_relevance_dict(
        question_text="Why is the sky blue?",
        actual_answer="Oxygen makes it blue"
    )

    assert isinstance(result["answer_relevance"], float)
    assert 0 <= result["answer_relevance"] <= 1
