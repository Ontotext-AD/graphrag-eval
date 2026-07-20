from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from pytest import raises

<<<<<<< HEAD
from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator


def test_extract_response_values_expected_case():
    response = "2\t3\t1\treason"
    result = AnswerCorrectnessEvaluator(ragas_llm=MagicMock()).extract_response_values(response)
    assert result == (2, 3, 1, "reason")
=======
from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator, AnswerCorrectnessResult
>>>>>>> 01e96e5 (answer_correctness to output JSON)


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
<<<<<<< HEAD
def test_extract_response_values_invalid_values(n_ref: int, n_actual: int, n_matching: int):
    response = f"{n_ref}\t{n_actual}\t{n_matching}\treason"
    with raises(ValueError,
                match=f"Invalid claims counts combination: {n_ref}\t{n_actual}\t{n_matching}"):
        AnswerCorrectnessEvaluator(ragas_llm=MagicMock()).extract_response_values(response)
=======
def test_answer_correctness_result_invalid_values(values):
    with raises(ValidationError):
        AnswerCorrectnessResult(**values)
>>>>>>> 01e96e5 (answer_correctness to output JSON)


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
<<<<<<< HEAD
def test_extract_response_values_non_int(n_ref: Any, n_actual: Any, n_matching: Any):
    response = f"{n_ref}\t{n_actual}\t{n_matching}\treason"
    with raises(ValueError,
                match=re.escape(
                    f"Claims counts should be ints: ['{n_ref}', '{n_actual}', '{n_matching}', "
                    f"'reason']"
                )):
        AnswerCorrectnessEvaluator(ragas_llm=MagicMock()).extract_response_values(response)


def test_extract_response_values_too_few_values():
    response = "2\t2\treason"
    with raises(ValueError, match=f"Expected 4 tab-separated values: {response}"):
        AnswerCorrectnessEvaluator(ragas_llm=MagicMock()).extract_response_values(response)


def test_extract_response_values_too_many_values():
    response = "2\t2\t2\treason\textra"
    result = AnswerCorrectnessEvaluator(ragas_llm=MagicMock()).extract_response_values(response)
    assert result == (2, 2, 2, "reason")
=======
def test_answer_correctness_result_valid_values(values):
    result = AnswerCorrectnessResult(**values)
    assert result.model_dump() == values
>>>>>>> 01e96e5 (answer_correctness to output JSON)
