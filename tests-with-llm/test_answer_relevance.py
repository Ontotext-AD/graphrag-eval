import os
from unittest.mock import AsyncMock, MagicMock

import pytest

from graphrag_eval import llm


def get_llm_config():
    return llm.Config(
        generation=llm.GenerationConfig(
            provider="openai",
            name="gpt-4o-mini",
            temperature=0.0,
            max_tokens=1024,
        ),
        embedding=llm.EmbeddingConfig(
            provider="openai",
            name="text-embedding-ada-002",
        )
    )



@pytest.fixture(scope="session", autouse=True)
def set_env():
    os.environ["OPENAI_API_KEY"] = "fake-key"


@pytest.mark.asyncio
async def test_get_relevance_dict_eval_success(monkeypatch):
    from graphrag_eval.answer_relevance import AnswerRelevancy, get_relevance_dict
    relevance_mock = AsyncMock(return_value=MagicMock(value=0.9))
    monkeypatch.setattr(AnswerRelevancy, 'ascore', relevance_mock)
    eval_result_dict = await get_relevance_dict(
        "Why is the sky blue?",
        "Because of the oxygen in the air",
        llm_config=get_llm_config(),
    )
    assert eval_result_dict == {
        "answer_relevance": 0.9
    }


@pytest.mark.asyncio
async def test_get_relevance_dict_eval_error(monkeypatch):
    from graphrag_eval.answer_relevance import AnswerRelevancy, get_relevance_dict
    relevance_mock = AsyncMock(side_effect=Exception("some error"))
    monkeypatch.setattr(AnswerRelevancy, 'ascore', relevance_mock)
    eval_result_dict = await get_relevance_dict(
        "Why is the sky blue?",
        "Because of the oxygen in the air",
        llm_config=get_llm_config(),
    )
    assert eval_result_dict == {
        "answer_relevance_error": "some error"
    }
