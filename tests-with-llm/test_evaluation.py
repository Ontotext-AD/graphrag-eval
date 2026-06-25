from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import yaml
from ragas.embeddings.base import BaseRagasEmbedding
from ragas.llms.base import InstructorBaseRagasLLM

from graphrag_eval import (
    compute_aggregates,
    run_evaluation,
)
from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator
from graphrag_eval.answer_relevance import AnswerRelevanceEvaluator
from tests.util import read_responses

DATA_DIR = Path(__file__).parent / "test_data"
CONFIG_FILE_PATH = DATA_DIR / "config-openai.yaml"


def mock_answer_correctness_evaluator(monkeypatch):
    async def mock_agenerate_correctness(self, prompt):
        return "2\t2\t2\tanswer correctness reason"

    monkeypatch.setattr(
        AnswerCorrectnessEvaluator,
        "_agenerate",
        mock_agenerate_correctness
    )


@pytest.mark.asyncio
async def test_run_evaluation_and_compute_aggregates(monkeypatch):
    async_mock = AsyncMock(return_value=MagicMock(value=0.9))

    from ragas.metrics.collections import AnswerRelevancy
    monkeypatch.setattr(AnswerRelevancy, "ascore", async_mock)

    from graphrag_eval.steps.retrieval_answer import (
        ContextRecall,
        ContextPrecision
    )
    monkeypatch.setattr(ContextRecall, "ascore", async_mock)
    monkeypatch.setattr(ContextPrecision, "ascore", async_mock)
    mock_answer_correctness_evaluator(monkeypatch)

    def mock_init_evaluators(_):
        mock_llm = MagicMock(spec=InstructorBaseRagasLLM)
        evaluators = []
        answer_relevance_evaluator = AnswerRelevanceEvaluator(
            mock_llm,
            MagicMock(spec=BaseRagasEmbedding)
        )
        evaluators.append(answer_relevance_evaluator)
        answer_correctness_evaluator = AnswerCorrectnessEvaluator(
            ragas_llm=mock_llm
        )
        evaluators.append(answer_correctness_evaluator)
        return evaluators, mock_llm

    from graphrag_eval import evaluation
    monkeypatch.setattr(
        evaluation,
        "parse_config_and_init_evaluators",
        mock_init_evaluators
    )

    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    actual_responses = read_responses(DATA_DIR / "actual_responses_1.jsonl")
    evaluation_results = await run_evaluation(
        reference_data,
        actual_responses,
        CONFIG_FILE_PATH,
    )
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_1.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results

    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_1.yaml").read_text(encoding="utf-8")
    )
    aggregates = compute_aggregates(evaluation_results, CONFIG_FILE_PATH)
    assert expected_aggregates == aggregates


@pytest.mark.asyncio
async def test_run_evaluation_and_compute_aggregates_no_actual_steps(
    monkeypatch
):
    async_mock = AsyncMock(return_value=MagicMock(value=0.9))

    from ragas.metrics.collections import AnswerRelevancy
    monkeypatch.setattr(AnswerRelevancy, "ascore", async_mock)
    mock_answer_correctness_evaluator(monkeypatch)

    def mock_init_evaluators(_):
        mock_llm = MagicMock(spec=InstructorBaseRagasLLM)
        evaluators = []
        answer_relevance_evaluator = AnswerRelevanceEvaluator(
            mock_llm,
            MagicMock(spec=BaseRagasEmbedding)
        )
        evaluators.append(answer_relevance_evaluator)
        answer_correctness_evaluator = AnswerCorrectnessEvaluator(
            ragas_llm=mock_llm
        )
        evaluators.append(answer_correctness_evaluator)

        return evaluators, mock_llm

    from graphrag_eval import evaluation
    monkeypatch.setattr(
        evaluation,
        "parse_config_and_init_evaluators",
        mock_init_evaluators
    )

    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    actual_responses = read_responses(DATA_DIR / "actual_responses_3.jsonl")
    evaluation_results = await run_evaluation(
        reference_data,
        actual_responses,
        CONFIG_FILE_PATH
    )
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_3.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_3.yaml").read_text(encoding="utf-8")
    )
    aggregates = compute_aggregates(evaluation_results, CONFIG_FILE_PATH)
    assert expected_aggregates == aggregates


@pytest.mark.asyncio
async def test_run_evaluation_and_compute_aggregates_all_errors():
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    actual_responses = read_responses(DATA_DIR / "actual_responses_2.jsonl")
    evaluation_results = await run_evaluation(
        reference_data,
        actual_responses,
        CONFIG_FILE_PATH
    )
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_2.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_2.yaml").read_text(encoding="utf-8")
    )
    aggregates = compute_aggregates(evaluation_results, CONFIG_FILE_PATH)
    assert expected_aggregates == aggregates


@pytest.mark.asyncio
async def test_answer_correctness_disabled(monkeypatch):
    async_mock = AsyncMock(return_value=MagicMock(value=0.9))

    from ragas.metrics.collections import AnswerRelevancy
    monkeypatch.setattr(AnswerRelevancy, "ascore", async_mock)

    def mock_init_evaluators(_):
        mock_llm = MagicMock(spec=InstructorBaseRagasLLM)
        answer_relevance_evaluator = AnswerRelevanceEvaluator(
            mock_llm,
            MagicMock(spec=BaseRagasEmbedding)
        )
        return [answer_relevance_evaluator], mock_llm

    from graphrag_eval import evaluation
    monkeypatch.setattr(
        evaluation,
        "parse_config_and_init_evaluators",
        mock_init_evaluators
    )

    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    actual_responses = read_responses(DATA_DIR / "actual_responses_3.jsonl")
    evaluation_results = await run_evaluation(
        reference_data,
        actual_responses,
        CONFIG_FILE_PATH
    )
    assert len(evaluation_results) > 0
    for res in evaluation_results:
        assert "answer_relevance" in res
        assert "answer_f1" not in res


@pytest.mark.asyncio
async def test_answer_relevance_disabled(monkeypatch):
    mock_answer_correctness_evaluator(monkeypatch)

    def mock_init_evaluators(_):
        mock_llm = MagicMock(spec=InstructorBaseRagasLLM)
        answer_correctness_evaluator = AnswerCorrectnessEvaluator(
            ragas_llm=mock_llm
        )
        return [answer_correctness_evaluator], mock_llm

    from graphrag_eval import evaluation
    monkeypatch.setattr(
        evaluation,
        "parse_config_and_init_evaluators",
        mock_init_evaluators
    )

    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    actual_responses = read_responses(DATA_DIR / "actual_responses_3.jsonl")
    evaluation_results = await run_evaluation(
        reference_data,
        actual_responses,
        CONFIG_FILE_PATH
    )
    assert len(evaluation_results) > 0
    for res in evaluation_results:
        assert "answer_f1" in res
        assert "answer_relevance" not in res


@pytest.mark.asyncio
async def test_answer_correctness_and_answer_relevance_disabled(monkeypatch):
    def mock_init_evaluators(_):
        return [], MagicMock(spec=InstructorBaseRagasLLM)

    from graphrag_eval import evaluation
    monkeypatch.setattr(
        evaluation,
        "parse_config_and_init_evaluators",
        mock_init_evaluators
    )

    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    actual_responses = read_responses(DATA_DIR / "actual_responses_3.jsonl")
    evaluation_results = await run_evaluation(
        reference_data,
        actual_responses,
        CONFIG_FILE_PATH
    )
    assert len(evaluation_results) > 0
    for res in evaluation_results:
        assert "answer_f1" not in res
        assert "answer_relevance" not in res
