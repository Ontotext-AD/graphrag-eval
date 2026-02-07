from pathlib import Path

import yaml
from langevals_ragas.lib.common import RagasResult, Money

from graphrag_eval import (
    compute_aggregates,
    run_evaluation,
)
from graphrag_eval.steps.retrieval_answer import (
    RagasResponseContextRecallEvaluator,
    RagasResponseContextPrecisionEvaluator,
)
from graphrag_eval.steps.retrieval_context_texts import (
    RagasContextPrecisionEvaluator,
    RagasContextRecallEvaluator,
)
from graphrag_eval.answer_relevance import RagasResponseRelevancyEvaluator
from tests.util import read_responses
from graphrag_eval import llm


DATA_DIR = Path(__file__).parent / "test_data"
CONFIG_FILE_PATH = DATA_DIR / "config-llm.yaml"


def test_run_evaluation_and_compute_aggregates(monkeypatch):
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    monkeypatch.setattr(
        RagasResponseRelevancyEvaluator,
        'evaluate',
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="answer relevance reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        RagasResponseContextRecallEvaluator,
        "evaluate",
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="retrieval answer recall reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        RagasResponseContextPrecisionEvaluator,
        "evaluate",
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="retrieval answer precision reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        RagasContextRecallEvaluator,
        "evaluate",
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="retrieval context recall reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        RagasContextPrecisionEvaluator,
        "evaluate",
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="retrieval context precision reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        llm,
        "call",
        lambda *_: "2\t2\t2\tanswer correctness reason"
    )

    actual_responses = read_responses(DATA_DIR / "actual_responses_1.jsonl")
    evaluation_results = run_evaluation(
        reference_data, 
        actual_responses,
        CONFIG_FILE_PATH
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


def test_run_evaluation_and_compute_aggregates_no_actual_steps(monkeypatch):
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    monkeypatch.setattr(
        RagasResponseRelevancyEvaluator,
        'evaluate',
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="answer relevance reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        llm,
        "call",
        lambda *_: "2\t2\t2\tanswer correctness reason"
    )

    actual_responses = read_responses(DATA_DIR / "actual_responses_3.jsonl")
    evaluation_results = run_evaluation(
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


def test_run_evaluation_and_compute_aggregates_all_errors():
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    actual_responses = read_responses(DATA_DIR / "actual_responses_2.jsonl")
    evaluation_results = run_evaluation(
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
