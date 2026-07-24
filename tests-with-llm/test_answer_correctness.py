from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from pytest import raises

from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator, AnswerCorrectnessResult


@pytest.mark.parametrize(
    "question, reference_answer, actual_answer",
    [
        ("Is Sofia the capital of Bulgaria?", "Yes", ""),
        ("Is Sofia the capital of Bulgaria?", "Yes", " "),
        ("Is Sofia the capital of Bulgaria?", "Yes", "\n\t  \r"),
        ("Is Sofia the capital of Bulgaria?", "", "No"),
        ("Is Sofia the capital of Bulgaria?", " ", "No"),
        ("Is Sofia the capital of Bulgaria?", "\n\t  \r", "No"),
        ("", "Yes", "No"),
        (" ", "Yes", "No"),
        ("\n\t  \r", "Yes", "No"),
        ("", "Yes", ""),
        ("", "", "No"),
        ("", "", ""),
    ],
)
@pytest.mark.asyncio
async def test_evaluate_answer_empty_strings(
    question: str, reference_answer: str, actual_answer: str
):
    with raises(ValueError, match="The question of the reference or the actual answer is a blank "
                                  "string!"):
        await AnswerCorrectnessEvaluator(ragas_llm=MagicMock()).evaluate_answer(
            question, reference_answer, actual_answer
        )


@pytest.mark.parametrize(
    "values",
    [
        {
            "reference_claims_count": 0,
            "actual_claims_count": 1,
            "matching_claims_count": 1,
            "reason": "reason",
        },
        {
            "reference_claims_count": 1,
            "actual_claims_count": 0,
            "matching_claims_count": 1,
            "reason": "reason",
        },
        {
            "reference_claims_count": 1,
            "actual_claims_count": 2,
            "matching_claims_count": -1,
            "reason": "reason",
        },
        {
            "reference_claims_count": 1,
            "actual_claims_count": 3,
            "matching_claims_count": 2,
            "reason": "reason",
        },
        {
            "reference_claims_count": 3,
            "actual_claims_count": 1,
            "matching_claims_count": 2,
            "reason": "reason",
        },
        {
            "reference_claims_count": 1,
            "actual_claims_count": 1,
            "matching_claims_count": 1,
            "reason": "",
        },
    ],
)
def test_answer_correctness_result_invalid_values(values):
    with raises(ValidationError):
        AnswerCorrectnessResult(**values)


@pytest.mark.parametrize(
    "values",
    [
        {
            "reference_claims_count": 1,
            "actual_claims_count": 1,
            "matching_claims_count": 1,
            "reason": "Perfect match.",
        },
        {
            "reference_claims_count": 2,
            "actual_claims_count": 3,
            "matching_claims_count": 0,
            "reason": "No claims match.",
        },
    ],
)
def test_answer_correctness_result_valid_values(values):
    result = AnswerCorrectnessResult(**values)
    assert result.model_dump() == values
