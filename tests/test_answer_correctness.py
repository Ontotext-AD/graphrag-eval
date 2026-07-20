import pytest
from pydantic import ValidationError

from graphrag_eval.answer_correctness import (
    AnswerCorrectnessEvaluator,
    AnswerCorrectnessResult,
)


class FakeLLM:
    def __init__(self, response):
        self.response = response
        self.prompt = None
        self.response_model = None

    async def agenerate(self, prompt, response_model):
        self.prompt = prompt
        self.response_model = response_model
        return self.response


@pytest.mark.asyncio
async def test_evaluate_answer_uses_structured_output_model():
    response = AnswerCorrectnessResult(
        reference_claims_count=2,
        actual_claims_count=3,
        matching_claims_count=1,
        reason="One claim matches.",
    )
    llm = FakeLLM(response)
    evaluator = AnswerCorrectnessEvaluator(llm=llm)

    result = await evaluator.evaluate_answer(
        question="What happened?",
        reference_answer="A and B happened.",
        actual_answer="A happened, plus C and D.",
    )

    assert result == response
    assert llm.response_model is AnswerCorrectnessResult
    assert llm.prompt is not None
    assert "What happened?" in llm.prompt


@pytest.mark.asyncio
async def test_get_correctness_dict_maps_structured_output_to_metrics():
    llm = FakeLLM({
        "reference_claims_count": 2,
        "actual_claims_count": 4,
        "matching_claims_count": 1,
        "reason": "One claim matches.",
    })
    evaluator = AnswerCorrectnessEvaluator(llm=llm)

    result = await evaluator.get_correctness_dict(
        reference={
            "question_text": "What happened?",
            "reference_answer": "A and B happened.",
        },
        actual={"actual_answer": "A happened, plus C and D."},
    )

    assert result == {
        "reference_answer": "A and B happened.",
        "answer_reference_claims_count": 2,
        "answer_actual_claims_count": 4,
        "answer_matching_claims_count": 1,
        "answer_correctness_reason": "One claim matches.",
        "answer_recall": 0.5,
        "answer_precision": 0.25,
        "answer_f1": 1 / 3,
    }


def test_structured_output_rejects_invalid_claim_count_combinations():
    with pytest.raises(ValidationError):
        AnswerCorrectnessResult(
            reference_claims_count=1,
            actual_claims_count=1,
            matching_claims_count=2,
            reason="Impossible count.",
        )
