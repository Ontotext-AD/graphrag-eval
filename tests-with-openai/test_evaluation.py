from pathlib import Path

import yaml
from graphrag_eval.custom_evaluation import CustomEvaluator
from langevals_ragas.lib.common import RagasResult, Money

from graphrag_eval import (
    answer_correctness,
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
from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator
from tests.util import read_responses


DATA_DIR = Path(__file__).parent / "test_data"


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
    evaluation_results = run_evaluation(reference_data, actual_responses)
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_1.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results

    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_1.yaml").read_text(encoding="utf-8")
    )
    aggregates = compute_aggregates(evaluation_results)
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
    evaluation_results = run_evaluation(reference_data, actual_responses)
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_3.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_3.yaml").read_text(encoding="utf-8")
    )
    aggregates = compute_aggregates(evaluation_results)
    assert expected_aggregates == aggregates


def test_run_evaluation_and_compute_aggregates_all_errors():
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    actual_responses = read_responses(DATA_DIR / "actual_responses_2.jsonl")
    evaluation_results = run_evaluation(reference_data, actual_responses)
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_2.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_2.yaml").read_text(encoding="utf-8")
    )
    aggregates = compute_aggregates(evaluation_results)
    assert expected_aggregates == aggregates


def test_run_custom_evaluation_ok(monkeypatch):
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
        answer_correctness,
        "OpenAI",
        lambda: None
    )
    monkeypatch.setattr(
        AnswerCorrectnessEvaluator,
        "call_llm",
        lambda *_: "2\t2\t2\tanswer correctness reason"
    )
    monkeypatch.setattr(
        CustomEvaluator,
        "call_llm",
        lambda *_: \
            "0.1\tCustom answer reason" \
            "\t0.2\tCustom context reason" \
            "\t0.3\tCustom steps reason"
    )
    actual_responses = read_responses(DATA_DIR / "actual_responses_1.jsonl")
    custom_eval_config_file_path = DATA_DIR / "custom-eval-config.yaml"
    evaluation_results = run_evaluation(
        reference_data, 
        actual_responses, 
        custom_eval_config_file_path
    )
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_4.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results


def test_run_custom_evaluation_eval_output_error(monkeypatch):
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
        answer_correctness,
        "OpenAI",
        lambda: None
    )
    monkeypatch.setattr(
        AnswerCorrectnessEvaluator,
        "call_llm",
        lambda *_: "2\t2\t2\tanswer correctness reason"
    )
    monkeypatch.setattr(
        CustomEvaluator,
        "call_llm",
        lambda *_: \
            "0.1\tCustom answer reason"
    )
    actual_responses = read_responses(DATA_DIR / "actual_responses_1.jsonl")
    custom_eval_config_file_path = DATA_DIR / "custom-eval-config.yaml"
    evaluation_results = run_evaluation(
        reference_data, 
        actual_responses, 
        custom_eval_config_file_path
    )
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_5.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results

# TODO test custom logic:
# 1. Specified in config but missing from reference or actual inputs:
# 1.1. reference context
# 1.2. reference steps
# 1.3. actual context
# 1.4. actual steps
