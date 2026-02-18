import os
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

import pytest
import yaml

from graphrag_eval import (
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

    async_mock = AsyncMock(return_value=MagicMock(value=0.9))

    from graphrag_eval.answer_relevance import AnswerRelevancy
    monkeypatch.setattr(AnswerRelevancy, 'ascore', async_mock)

    from graphrag_eval.steps.retrieval_answer import (
        ContextRecall,
        ContextPrecision
    )
    monkeypatch.setattr(ContextRecall, 'ascore', async_mock)
    monkeypatch.setattr(ContextPrecision, 'ascore', async_mock)

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

    async_mock = AsyncMock(return_value=MagicMock(value=0.9))

    from graphrag_eval.answer_relevance import AnswerRelevancy
    monkeypatch.setattr(AnswerRelevancy, 'ascore', async_mock)

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
