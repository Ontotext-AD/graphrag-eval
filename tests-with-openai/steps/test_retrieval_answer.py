import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest import approx


@pytest.fixture(scope="session", autouse=True)
def set_env():
    os.environ["OPENAI_API_KEY"] = "fake-key"


@pytest.mark.asyncio
async def test_get_retrieval_evaluation_dict_success(monkeypatch):
    from graphrag_eval.steps import retrieval_answer

    mock_result_recall = MagicMock()
    mock_result_recall.value = 0.9
    monkeypatch.setattr(
        retrieval_answer.ContextRecall,
        'ascore',
        AsyncMock(return_value=mock_result_recall)
    )

    mock_result_precision = MagicMock()
    mock_result_precision.value = 0.6
    monkeypatch.setattr(
        retrieval_answer.ContextPrecision,
        'ascore',
        AsyncMock(return_value=mock_result_precision)
    )
    eval_result_dict = await retrieval_answer.get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_answer="Because of the oxygen in the air",
        actual_contexts=[{
            "id": "http://example.com/resource/doc/1",
            "text": "Oxygen turns the sky blue"
        }],
    )
    assert approx(eval_result_dict) == {
        "retrieval_answer_recall": 0.9,
        "retrieval_answer_precision": 0.6,
        "retrieval_answer_f1": 0.72,
    }


@pytest.mark.asyncio
async def test_get_retrieval_evaluation_dict_recall_error_precision_success(monkeypatch):
    from graphrag_eval.steps import retrieval_answer

    monkeypatch.setattr(
        retrieval_answer.ContextRecall,
        'ascore',
        AsyncMock(side_effect=Exception("some error"))
    )

    mock_result_precision = MagicMock()
    mock_result_precision.value = 0.6
    monkeypatch.setattr(
        retrieval_answer.ContextPrecision,
        'ascore',
        AsyncMock(return_value=mock_result_precision)
    )
    eval_result_dict = await retrieval_answer.get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_answer="Because of the oxygen in the air",
        actual_contexts=[{
            "id": "http://example.com/resource/doc/1",
            "text": "Oxygen turns the sky blue"
        }],
    )
    assert eval_result_dict == {
        "retrieval_answer_recall_error": "some error",
        "retrieval_answer_precision": 0.6,
    }


@pytest.mark.asyncio
async def test_get_retrieval_evaluation_dict_recall_success_precision_error(monkeypatch):
    from graphrag_eval.steps import retrieval_answer

    mock_result_recall = MagicMock()
    mock_result_recall.value = 0.9
    monkeypatch.setattr(
        retrieval_answer.ContextRecall,
        'ascore',
        AsyncMock(return_value=mock_result_recall)
    )

    monkeypatch.setattr(
        retrieval_answer.ContextPrecision,
        'ascore',
        AsyncMock(side_effect=Exception("some error"))
    )
    eval_result_dict = await retrieval_answer.get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_answer="Because of the oxygen in the air",
        actual_contexts=[{
            "id": "http://example.com/resource/doc/1",
            "text": "Oxygen turns the sky blue"
        }],
    )
    assert eval_result_dict == {
        "retrieval_answer_recall": 0.9,
        "retrieval_answer_precision_error": "some error"
    }


@pytest.mark.asyncio
async def test_get_retrieval_evaluation_dict_both_errors(monkeypatch):
    from graphrag_eval.steps import retrieval_answer

    monkeypatch.setattr(
        retrieval_answer.ContextRecall,
        'ascore',
        AsyncMock(side_effect=Exception("some error"))
    )

    monkeypatch.setattr(
        retrieval_answer.ContextPrecision,
        'ascore',
        AsyncMock(side_effect=Exception("some error"))
    )
    eval_result_dict = await retrieval_answer.get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_answer="Because of the oxygen in the air",
        actual_contexts=[{
            "id": "http://example.com/resource/doc/1",
            "text": "Oxygen turns the sky blue"
        }],
    )
    assert eval_result_dict == {
        "retrieval_answer_recall_error": "some error",
        "retrieval_answer_precision_error": "some error"
    }
