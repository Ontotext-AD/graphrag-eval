import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from ragas.llms.base import InstructorBaseRagasLLM

from graphrag_eval.answer_relevance import AnswerRelevanceEvaluator


def get_ragas_llm() -> InstructorBaseRagasLLM:
    from openai import AsyncOpenAI
    from ragas.llms import llm_factory

    return llm_factory("gpt-3.5-turbo", client=AsyncOpenAI())


def get_ragas_embedder():
    from openai import AsyncOpenAI
    from ragas.embeddings.base import embedding_factory

    return embedding_factory("openai", client=AsyncOpenAI())


@pytest.fixture(scope="session", autouse=True)
def set_env():
    os.environ["OPENAI_API_KEY"] = "fake-key"


@pytest.mark.asyncio
async def test_evaluate_answer_relevance_success(monkeypatch):
    async_mock = AsyncMock(return_value=MagicMock(value=0.9))
    from ragas.metrics.collections import AnswerRelevancy
    monkeypatch.setattr(AnswerRelevancy, "ascore", async_mock)

    evaluator = AnswerRelevanceEvaluator(get_ragas_llm(), get_ragas_embedder())
    eval_result_dict = await evaluator.evaluate(
        {"question_text": "Why is the sky blue?"},
        {"actual_answer": "Because of the oxygen in the air"},
    )
    assert eval_result_dict == {
        "answer_relevance": 0.9
    }


@pytest.mark.asyncio
async def test_evaluate_answer_relevance_error(monkeypatch):
    async_mock = AsyncMock(side_effect=Exception("some error"))
    from ragas.metrics.collections import AnswerRelevancy
    monkeypatch.setattr(AnswerRelevancy, 'ascore', async_mock)

    evaluator = AnswerRelevanceEvaluator(get_ragas_llm(), get_ragas_embedder())
    eval_result_dict = await evaluator.evaluate(
        {"question_text": "Why is the sky blue?"},
        {"actual_answer": "Because of the oxygen in the air"},
    )
    assert eval_result_dict == {
        "answer_relevance_error": "some error"
    }
