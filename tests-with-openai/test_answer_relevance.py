import os
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture(scope="session", autouse=True)
def set_env():
    os.environ["OPENAI_API_KEY"] = "fake-key"


@pytest.mark.asyncio
async def test_get_relevance_dict_eval_success(monkeypatch):
    from graphrag_eval import answer_relevance

    mock_result = MagicMock()
    mock_result.value = 0.9

    monkeypatch.setattr(
        answer_relevance.AnswerRelevancy,
        'ascore',
        AsyncMock(return_value=mock_result)
    )
    eval_result_dict = await answer_relevance.get_relevance_dict(
        "Why is the sky blue?",
        "Because of the oxygen in the air"
    )
    assert eval_result_dict == {
        "answer_relevance": 0.9
    }


@pytest.mark.asyncio
async def test_get_relevance_dict_eval_error(monkeypatch):
    from graphrag_eval import answer_relevance

    monkeypatch.setattr(
        answer_relevance.AnswerRelevancy,
        'ascore',
        AsyncMock(side_effect=Exception("some error"))
    )
    eval_result_dict = await answer_relevance.get_relevance_dict(
        "Why is the sky blue?",
        "Because of the oxygen in the air"
    )
    assert eval_result_dict == {
        "answer_relevance_error": "some error"
    }
