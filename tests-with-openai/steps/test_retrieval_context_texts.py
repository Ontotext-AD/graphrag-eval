import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest import approx


@pytest.fixture(scope="session", autouse=True)
def set_env():
    os.environ["OPENAI_API_KEY"] = "fake-key"


context_1_dict = {
    "id": "1",
    "text": "Oxygen turns the sky blue"
}


@pytest.mark.asyncio
async def test_get_retrieval_evaluation_dict_success(monkeypatch):
    from graphrag_eval.steps.retrieval_context_texts import (
        ContextRecall,
        ContextPrecision,
        get_retrieval_evaluation_dict
    )
    recall_mock = AsyncMock(return_value=MagicMock(value=0.9))
    monkeypatch.setattr(ContextRecall, 'ascore', recall_mock)
    precision_mock = AsyncMock(return_value=MagicMock(value=0.6))
    monkeypatch.setattr(ContextPrecision, 'ascore', precision_mock)

    eval_result_dict = await get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_contexts=[context_1_dict],
        actual_contexts=[context_1_dict],
    )
    assert approx(eval_result_dict) == {
        "retrieval_context_recall": 0.9,
        "retrieval_context_precision": 0.6,
        "retrieval_context_f1": 0.72,
    }


@pytest.mark.asyncio
async def test_get_retrieval_evaluation_dict_recall_error(monkeypatch):
    from graphrag_eval.steps.retrieval_context_texts import (
        ContextRecall,
        ContextPrecision,
        get_retrieval_evaluation_dict
    )
    recall_mock = AsyncMock(side_effect=Exception("recall error"))
    monkeypatch.setattr(ContextRecall, 'ascore', recall_mock)
    precision_mock = AsyncMock(return_value=MagicMock(value=0.6))
    monkeypatch.setattr(ContextPrecision, 'ascore', precision_mock)

    eval_result_dict = await get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_contexts=[context_1_dict],
        actual_contexts=[context_1_dict],
    )
    assert eval_result_dict == {
        "retrieval_context_recall_error": "recall error",
        "retrieval_context_precision": 0.6,
    }

@pytest.mark.asyncio
async def test_get_retrieval_evaluation_dict_precision_error(monkeypatch):
    from graphrag_eval.steps.retrieval_context_texts import (
        ContextRecall,
        ContextPrecision,
        get_retrieval_evaluation_dict
    )
    recall_mock = AsyncMock(return_value=MagicMock(value=0.9))
    monkeypatch.setattr(ContextRecall, 'ascore', recall_mock)
    precision_mock = AsyncMock(side_effect=Exception("precision error"))
    monkeypatch.setattr(ContextPrecision, 'ascore', precision_mock)
    
    eval_result_dict = await get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_contexts=[context_1_dict],
        actual_contexts=[context_1_dict],
    )
    assert eval_result_dict == {
        "retrieval_context_recall": 0.9,
        "retrieval_context_precision_error": "precision error",
    }


@pytest.mark.asyncio
async def test_get_retrieval_evaluation_dict_both_error(monkeypatch):
    from graphrag_eval.steps.retrieval_context_texts import (
        ContextRecall,
        ContextPrecision,
        get_retrieval_evaluation_dict
    )
    recall_mock = AsyncMock(side_effect=Exception("recall error"))
    monkeypatch.setattr(ContextRecall, 'ascore', recall_mock)
    precision_mock = AsyncMock(side_effect=Exception("precision error"))
    monkeypatch.setattr(ContextPrecision, 'ascore', precision_mock)
    
    eval_result_dict = await get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_contexts=[context_1_dict],
        actual_contexts=[context_1_dict],
    )
    assert eval_result_dict == {
        "retrieval_context_recall_error": "recall error",
        "retrieval_context_precision_error": "precision error",
    }
