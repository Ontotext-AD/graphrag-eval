import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest import approx


@pytest.fixture(scope="session", autouse=True)
def set_env():
    os.environ["OPENAI_API_KEY"] = "fake-key"


@pytest.mark.asyncio
async def test_get_retrieval_evaluation_dict_success(monkeypatch):
    from graphrag_eval.steps.retrieval_answer import (
        ContextRecall,
        ContextPrecision,
        get_retrieval_evaluation_dict,
    )
    recall_mock = AsyncMock(return_value=MagicMock(value=0.9))
    monkeypatch.setattr(ContextRecall, 'ascore', recall_mock)
    precision_mock = AsyncMock(return_value=MagicMock(value=0.6))
    monkeypatch.setattr(ContextPrecision, 'ascore', precision_mock)

    eval_result_dict = await get_retrieval_evaluation_dict(
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
    from graphrag_eval.steps.retrieval_answer import (
        ContextRecall,
        ContextPrecision,
        get_retrieval_evaluation_dict,
    )
    recall_mock = AsyncMock(side_effect=Exception("some error"))
    monkeypatch.setattr(ContextRecall, 'ascore', recall_mock)
    precision_mock = AsyncMock(return_value=MagicMock(value=0.6))
    monkeypatch.setattr(ContextPrecision, 'ascore', precision_mock)
    
    eval_result_dict = await get_retrieval_evaluation_dict(
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
    from graphrag_eval.steps.retrieval_answer import (
        ContextRecall,
        ContextPrecision,
        get_retrieval_evaluation_dict
    )
    context_recall = AsyncMock(return_value= MagicMock(value=0.9))
    monkeypatch.setattr(ContextRecall, 'ascore', context_recall)
    context_precision = AsyncMock(side_effect=Exception("some error"))
    monkeypatch.setattr(ContextPrecision, 'ascore', context_precision)

    eval_result_dict = await get_retrieval_evaluation_dict(
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
    from graphrag_eval.steps.retrieval_answer import (
        ContextRecall,
        ContextPrecision,
        get_retrieval_evaluation_dict,
    )
    recall_mock = AsyncMock(side_effect=Exception("some error"))
    monkeypatch.setattr(ContextRecall, 'ascore', recall_mock)
    precision_mock = AsyncMock(side_effect=Exception("other error"))
    monkeypatch.setattr(ContextPrecision, 'ascore', precision_mock)

    eval_result_dict = await get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_answer="Because of the oxygen in the air",
        actual_contexts=[{
            "id": "http://example.com/resource/doc/1",
            "text": "Oxygen turns the sky blue"
        }],
    )
    assert eval_result_dict == {
        "retrieval_answer_recall_error": "some error",
        "retrieval_answer_precision_error": "other error"
    }
