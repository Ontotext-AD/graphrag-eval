import csv
from unittest.mock import MagicMock, AsyncMock, patch

import pytest
import yaml

from graphrag_eval.answer_correctness import InvalidPromptException
from graphrag_eval.cli.answer_correctness import evaluate_and_write, run


@pytest.mark.asyncio
async def test_evaluate_and_write_success(tmp_path):
    input_file = tmp_path / "input.tsv"
    output_file = tmp_path / "output.tsv"

    input_headers = ["Question", "Reference answer", "Actual answer"]
    input_rows = [
        {
            "Question": "What is Python?",
            "Reference answer": "A language.",
            "Actual answer": "A programming language."
        },
        {
            "Question": "What is 2+2?",
            "Reference answer": "4",
            "Actual answer": "4"
        },
        {
            "Question": "Is Sofia the capital of Bulgaria?",
            "Reference answer": "Yes",
            "Actual answer": ""
        },
        {
            "Question": "Why is the sky blue?",
            "Reference answer": "In Rayleigh scattering, shorter wavelengths are scattered more",
            "Actual answer": "Gases scatter sunlight"
        },
    ]

    with open(input_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=input_headers, delimiter="\t")
        writer.writeheader()
        writer.writerows(input_rows)

    mock_evaluator = MagicMock()

    mock_evaluator.evaluate_answer = AsyncMock()
    mock_evaluator.evaluate_answer.side_effect = [
        ("1", "1", "1", "Good match"),
        ("1", "1", "1", "Perfect match"),
        ValueError("The question of the reference or the actual answer is a blank string!"),
        Exception("LLM Timeout Error"),
    ]

    await evaluate_and_write(
        input_tsv_file_path=input_file,
        output_tsv_file_path=output_file,
        evaluator=mock_evaluator
    )

    assert mock_evaluator.evaluate_answer.call_count == 4
    mock_evaluator.evaluate_answer.assert_any_call(
        "What is Python?",
        "A language.",
        "A programming language."
    )
    mock_evaluator.evaluate_answer.assert_any_call(
        "What is 2+2?",
        "4",
        "4"
    )
    mock_evaluator.evaluate_answer.assert_any_call(
        "Is Sofia the capital of Bulgaria?",
        "Yes",
        ""
    )
    mock_evaluator.evaluate_answer.assert_any_call(
        "Why is the sky blue?",
        "In Rayleigh scattering, shorter wavelengths are scattered more",
        "Gases scatter sunlight"
    )

    with open(output_file, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        output_data = list(reader)

    expected_headers = ["#Reference", "#PTarget", "#Matching", "Reasoning", "Error"]
    assert output_data[0] == expected_headers
    assert output_data[1] == ["1", "1", "1", "Good match", ""]
    assert output_data[2] == ["1", "1", "1", "Perfect match", ""]
    assert output_data[3] == [
        "", "", "", "", "The question of the reference or the actual answer is a blank string!"
    ]
    assert output_data[4] == ["", "", "", "", "LLM Timeout Error"]


@pytest.mark.asyncio
async def test_evaluate_and_write_wrong_input_format(tmp_path):
    input_file = tmp_path / "corrupted_input.tsv"
    output_file = tmp_path / "output.tsv"

    wrong_headers = ["Question", "WrongColumn1", "WrongColumn2"]
    wrong_rows = [
        {"Question": "What is Python?", "WrongColumn1": "Some data", "WrongColumn2": "More data"}
    ]

    with open(input_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=wrong_headers, delimiter="\t")
        writer.writeheader()
        writer.writerows(wrong_rows)

    mock_evaluator = MagicMock()
    mock_evaluator.evaluate_answer = AsyncMock()

    with pytest.raises(ValueError, match="Unexpected input format!"):
        await evaluate_and_write(
            input_tsv_file_path=input_file,
            output_tsv_file_path=output_file,
            evaluator=mock_evaluator
        )

    mock_evaluator.evaluate_answer.assert_not_called()

    with open(output_file, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        output_data = list(reader)

    assert len(output_data) == 1
    assert output_data[0] == ["#Reference", "#PTarget", "#Matching", "Reasoning", "Error"]


@patch("graphrag_eval.cli.answer_correctness.llm_factory.create_llm")
def test_run_with_custom_prompt(mock_create_llm, tmp_path):
    config_path = tmp_path / "config.yaml"
    input_path = tmp_path / "input.tsv"
    output_path = tmp_path / "output.tsv"

    custom_prompt = """You are an expert evaluator assessing factual criteria...
{question}
{reference_answer}
{actual_answer}
"""
    config_data = {
        "llm": {"generation": {"provider": "openai", "model": "gpt-4o-mini"}},
        "answer_correctness": {"prompt": custom_prompt}
    }

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)

    with open(input_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["Question", "Reference answer", "Actual answer"])
        writer.writerow(["What is 1+1?", "2", "3"])

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="1\t1\t1\tThe response matches perfectly."))
    ]

    mock_llm = MagicMock()
    mock_llm.agenerate = AsyncMock(return_value=mock_response)
    mock_create_llm.return_value = mock_llm

    run(
        config_yaml_file_path=config_path,
        input_tsv_file_path=input_path,
        output_tsv_file_path=output_path
    )

    mock_create_llm.assert_called_once()
    called_prompt = mock_llm.agenerate.call_args[0][0]
    assert ("""You are an expert evaluator assessing factual criteria...
What is 1+1?
2
3
""" == called_prompt)

    assert output_path.exists()
    with open(output_path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        output_data = list(reader)

    assert output_data[0] == ["#Reference", "#PTarget", "#Matching", "Reasoning", "Error"]
    assert output_data[1] == ["1", "1", "1", "The response matches perfectly.", ""]


@patch("graphrag_eval.cli.answer_correctness.llm_factory.create_llm")
def test_run_with_invalid_prompt(mock_create_llm, tmp_path):
    config_path = tmp_path / "config.yaml"
    input_path = tmp_path / "input.tsv"
    output_path = tmp_path / "output.tsv"

    custom_prompt = "You are an expert evaluator assessing factual criteria...\\n{unexpected}\\n"
    config_data = {
        "llm": {"generation": {"provider": "openai", "model": "gpt-4o-mini"}},
        "answer_correctness": {"prompt": custom_prompt}
    }

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)

    with open(input_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["Question", "Reference answer", "Actual answer"])
        writer.writerow(["What is 1+1?", "2", "3"])

    mock_llm = MagicMock()
    mock_create_llm.return_value = mock_llm

    with pytest.raises(InvalidPromptException,
                       match="Invalid prompt template. Must only contain placeholders: "
                             "{question}, {reference_answer}, and {actual_answer}. Original "
                             "error: 'unexpected'"):
        run(
            config_yaml_file_path=config_path,
            input_tsv_file_path=input_path,
            output_tsv_file_path=output_path
        )

    mock_llm.agenerate.assert_not_called()
