import re
from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest import raises

from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator


def test_extract_response_values_expected_case():
    response = "2\t3\t1\treason"
    result = AnswerCorrectnessEvaluator(llm=MagicMock()).extract_response_values(response)
    assert result == (2, 3, 1, "reason")


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
        await AnswerCorrectnessEvaluator(llm=MagicMock()).evaluate_answer(
            question, reference_answer, actual_answer
        )


@pytest.mark.parametrize(
    "n_ref, n_actual, n_matching",
    [
        (0, 1, 1),
        (1, 0, 1),
        (15, 0, 0),
        (1, 2, -1),
        (1, 3, 2),
        (3, 1, 2)
    ],
)
def test_extract_response_values_invalid_values(n_ref: int, n_actual: int, n_matching: int):
    response = f"{n_ref}\t{n_actual}\t{n_matching}\treason"
    with raises(ValueError,
                match=f"Invalid claims counts combination: {n_ref}\t{n_actual}\t{n_matching}"):
        AnswerCorrectnessEvaluator(llm=MagicMock()).extract_response_values(response)


@pytest.mark.parametrize(
    "n_ref, n_actual, n_matching",
    [
        (1, 1, "x"),
        (1, "x", 1),
        (1, "x", "y"),
        ("x", 1, 1),
        ("x", 1, "y"),
        ("x", "y", 1),
        ("x", "y", "z"),
    ],
)
def test_extract_response_values_non_int(n_ref: Any, n_actual: Any, n_matching: Any):
    response = f"{n_ref}\t{n_actual}\t{n_matching}\treason"
    with raises(ValueError,
                match=re.escape(
                    f"Claims counts should be ints: ['{n_ref}', '{n_actual}', '{n_matching}', "
                    f"'reason']"
                )):
        AnswerCorrectnessEvaluator(llm=MagicMock()).extract_response_values(response)


def test_extract_response_values_too_few_values():
    response = "2\t2\treason"
    with raises(ValueError, match=f"Expected 4 tab-separated values: {response}"):
        AnswerCorrectnessEvaluator(llm=MagicMock()).extract_response_values(response)


def test_extract_response_values_too_many_values():
    response = "2\t2\t2\treason\textra"
    result = AnswerCorrectnessEvaluator(llm=MagicMock()).extract_response_values(response)
    assert result == (2, 2, 2, "reason")
