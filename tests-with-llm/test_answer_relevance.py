from collections import namedtuple

from graphrag_eval import answer_relevance
from langevals_ragas.lib.common import RagasResult, Money
from graphrag_eval import llm


llm_config = llm.Config(
    name="openai/gpt-4o-mini",
    temperature=0.0,
    max_tokens=1024,
)


def test_get_relevance_dict_eval_success(monkeypatch):
    monkeypatch.setattr(
        answer_relevance.RagasResponseRelevancyEvaluator,
        'evaluate',
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="relevance reason",
            cost=Money(
                currency="USD",
                amount=0.0007,
            )
        )
    )
    eval_result_dict = answer_relevance.get_relevance_dict(
        "Why is the sky blue?",
        "Because of the oxygen in the air",
        llm_config=llm_config,
    )
    assert eval_result_dict == {
        "answer_relevance": 0.9,
        "answer_relevance_cost": 0.0007,
        "answer_relevance_reason": "relevance reason",
    }


def test_get_relevance_dict_eval_error(monkeypatch):
    monkeypatch.setattr(
        answer_relevance.RagasResponseRelevancyEvaluator,
        'evaluate',
        lambda *_: namedtuple('RagasResult', ['status', 'details'])(
            status="error",
            details="details",
        )
    )
    eval_result_dict = answer_relevance.get_relevance_dict(
        "Why is the sky blue?",
        "Because of the oxygen in the air",
        llm_config=llm_config,
    )
    assert eval_result_dict == {
        "answer_relevance_error": "details"
    }
