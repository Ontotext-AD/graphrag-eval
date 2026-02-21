import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest import approx

from graphrag_eval import llm


@pytest.fixture(scope="session", autouse=True)
def set_env():
    os.environ["OPENAI_API_KEY"] = "fake-key"


def get_generation_config():
    return llm.GenerationConfig(
            provider="openai",
            name="gpt-4o-mini",
            temperature=0.0,
            max_tokens=1024,
        )


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
        generation_config=get_generation_config(),
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
        generation_config=get_generation_config(),
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
        generation_config=get_generation_config(),
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
        generation_config=get_generation_config(),
    )
    assert eval_result_dict == {
        "retrieval_context_recall_error": "recall error",
        "retrieval_context_precision_error": "precision error",
    }
