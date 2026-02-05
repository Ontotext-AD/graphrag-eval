import os
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

import pytest
import yaml

from graphrag_eval import (
    answer_correctness,
    compute_aggregates,
    run_evaluation,
)
from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator
from tests.util import read_responses

DATA_DIR = Path(__file__).parent / "test_data"


@pytest.fixture(scope="session", autouse=True)
def set_env():
    os.environ["OPENAI_API_KEY"] = "fake-key"


@pytest.mark.asyncio
async def test_run_evaluation_and_compute_aggregates(monkeypatch):
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )

    mock_result = MagicMock()
    mock_result.value = 0.9

    from graphrag_eval import answer_relevance
    monkeypatch.setattr(
        answer_relevance.AnswerRelevancy,
        'ascore',
        AsyncMock(return_value=mock_result)
    )

    from graphrag_eval.steps import retrieval_answer

    mock_result_recall = MagicMock()
    mock_result_recall.value = 0.9
    monkeypatch.setattr(
        retrieval_answer.ContextRecall,
        'ascore',
        AsyncMock(return_value=mock_result_recall)
    )

    mock_result_precision = MagicMock()
    mock_result_precision.value = 0.9
    monkeypatch.setattr(
        retrieval_answer.ContextPrecision,
        'ascore',
        AsyncMock(return_value=mock_result_precision)
    )

    from graphrag_eval.steps import retrieval_context_texts

    mock_result_recall = MagicMock()
    mock_result_recall.value = 0.9
    monkeypatch.setattr(
        retrieval_context_texts.ContextRecall,
        'ascore',
        AsyncMock(return_value=mock_result_recall)
    )
    monkeypatch.setattr(
        retrieval_context_texts.ContextPrecision,
        'ascore',
        AsyncMock(return_value=mock_result_recall)
    )

    monkeypatch.setattr(
        answer_correctness,
        "OpenAI",
        lambda: None
    )
    monkeypatch.setattr(
        AnswerCorrectnessEvaluator,
        "call_llm",
        lambda *_: "2\t2\t2\tanswer correctness reason"
    )

    actual_responses = read_responses(DATA_DIR / "actual_responses_1.jsonl")
    evaluation_results = await run_evaluation(reference_data, actual_responses)
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_1.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results

    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_1.yaml").read_text(encoding="utf-8")
    )
    aggregates = compute_aggregates(evaluation_results)
    assert expected_aggregates == aggregates


@pytest.mark.asyncio
async def test_run_evaluation_and_compute_aggregates_no_actual_steps(monkeypatch):
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )

    mock_result = MagicMock()
    mock_result.value = 0.9

    from graphrag_eval import answer_relevance
    monkeypatch.setattr(
        answer_relevance.AnswerRelevancy,
        'ascore',
        AsyncMock(return_value=mock_result)
    )
    monkeypatch.setattr(
        answer_correctness,
        "OpenAI",
        lambda: None
    )
    monkeypatch.setattr(
        AnswerCorrectnessEvaluator,
        "call_llm",
        lambda *_: "2\t2\t2\tanswer correctness reason"
    )

    actual_responses = read_responses(DATA_DIR / "actual_responses_3.jsonl")
    evaluation_results = await run_evaluation(reference_data, actual_responses)
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_3.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_3.yaml").read_text(encoding="utf-8")
    )
    aggregates = compute_aggregates(evaluation_results)
    assert expected_aggregates == aggregates


@pytest.mark.asyncio
async def test_run_evaluation_and_compute_aggregates_all_errors():
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    actual_responses = read_responses(DATA_DIR / "actual_responses_2.jsonl")
    evaluation_results = await run_evaluation(reference_data, actual_responses)
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_2.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_2.yaml").read_text(encoding="utf-8")
    )
    aggregates = compute_aggregates(evaluation_results)
    assert expected_aggregates == aggregates
