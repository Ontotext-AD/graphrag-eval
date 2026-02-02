from collections import namedtuple
from pytest import approx

from langevals_ragas.lib.common import RagasResult, Money

from graphrag_eval.steps.retrieval_context_texts import (
    RagasContextPrecisionEvaluator,
    RagasContextRecallEvaluator,
    get_retrieval_evaluation_dict,
)
from graphrag_eval import llm


llm_config = llm.Config(
    name="openai/gpt-4o-mini",
    temperature=0.0,
    max_tokens=1024,
)



context_1_dict = {
    "id": "1",
    "text": "Oxygen turns the sky blue"
}


def test_get_retrieval_evaluation_dict_success(monkeypatch):
    monkeypatch.setattr(
        RagasContextRecallEvaluator,
        'evaluate',
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="retrieval context recall reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        RagasContextPrecisionEvaluator,
        'evaluate',
        lambda *_: RagasResult(
            status="processed",
            score=0.6,
            details="retrieval context precision reason",
            cost=Money(currency="USD", amount=0.0003)
        )
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        reference_contexts=[context_1_dict],
        actual_contexts=[context_1_dict],
        llm_config=llm_config,
    )
    assert approx(eval_result_dict) == {
        "retrieval_context_recall": 0.9,
        "retrieval_context_recall_reason": "retrieval context recall reason",
        "retrieval_context_recall_cost": 0.0007,
        "retrieval_context_precision": 0.6,
        "retrieval_context_precision_reason": "retrieval context precision reason",
        "retrieval_context_precision_cost": 0.0003,
        "retrieval_context_f1": 0.72,
        "retrieval_context_f1_cost": 0.0010,
    }


def test_get_retrieval_evaluation_dict_recall_success_precision_error(monkeypatch):
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
        lambda *_: namedtuple("RagasResult", ["status", "details", "cost"])(
            status="error",
            details="retrieval context precision error",
            cost=Money(currency="USD", amount=0.0003)
        )
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        reference_contexts=[context_1_dict],
        actual_contexts=[context_1_dict],
        llm_config=llm_config,
    )
    assert eval_result_dict == {
        "retrieval_context_recall": 0.9,
        "retrieval_context_recall_reason": "retrieval context recall reason",
        "retrieval_context_recall_cost": 0.0007,
        "retrieval_context_precision_error": "retrieval context precision error"
    }


def test_get_retrieval_evaluation_dict_both_errors(monkeypatch):
    monkeypatch.setattr(
        RagasContextRecallEvaluator,
        "evaluate",
        lambda *_: namedtuple("RagasResult", ["status", "details", "cost"])(
            status="error",
            details="retrieval context recall error",
            cost=Money(currency="USD", amount=0.0003)
        )
    )
    monkeypatch.setattr(
        RagasContextPrecisionEvaluator,
        "evaluate",
        lambda *_: namedtuple("RagasResult", ["status", "details", "cost"])(
            status="error",
            details="retrieval context precision error",
            cost=Money(currency="USD", amount=0.0003)
        )
    )
    eval_result_dict = get_retrieval_evaluation_dict(
        reference_contexts=[context_1_dict],
        actual_contexts=[context_1_dict],
        llm_config=llm_config,
    )
    assert eval_result_dict == {
        "retrieval_context_recall_error": "retrieval context recall error",
        "retrieval_context_precision_error": "retrieval context precision error",
    }
