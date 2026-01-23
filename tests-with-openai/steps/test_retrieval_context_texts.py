import os
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture(scope="session", autouse=True)
def set_env():
    os.environ["OPENAI_API_KEY"] = "fake-key"


@pytest.mark.asyncio
async def test_get_retrieval_evaluation_dict_success(monkeypatch):
    from graphrag_eval.steps import retrieval_context_texts

    mock_result_recall = MagicMock()
    mock_result_recall.value = 0.9
    monkeypatch.setattr(
        retrieval_context_texts.ContextEntityRecall,
        'ascore',
        AsyncMock(return_value=mock_result_recall)
    )

    eval_result_dict = await retrieval_context_texts.get_retrieval_evaluation_dict(
        reference_answer="Oxygen turns the sky blue",
        actual_contexts=[{
            "id": "1",
            "text": "Oxygen turns the sky blue"
        }],
    )
    assert eval_result_dict == {
        "retrieval_context_recall": 0.9,
    }


@pytest.mark.asyncio
async def test_get_retrieval_evaluation_dict_error(monkeypatch):
    from graphrag_eval.steps import retrieval_context_texts

    monkeypatch.setattr(
        retrieval_context_texts.ContextEntityRecall,
        'ascore',
        AsyncMock(side_effect=Exception("some error"))
    )

    eval_result_dict = await retrieval_context_texts.get_retrieval_evaluation_dict(
        reference_answer="Oxygen turns the sky blue",
        actual_contexts=[{
            "id": "1",
            "text": "Oxygen turns the sky blue"
        }],
    )
    assert eval_result_dict == {
        "retrieval_context_recall_error": "some error"
    }
