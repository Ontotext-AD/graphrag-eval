import builtins
import io

from unittest.mock import MagicMock

from graphrag_eval import answer_correctness
from graphrag_eval import evaluation
from graphrag_eval.answer_correctness import (
    AnswerCorrectnessEvaluator,
    extract_response_values,
    llm,
)


def get_llm_config():
    return evaluation.Config(
        llm=llm.Config(
            generation=llm.GenerationConfig(
                provider="openai",
                model="gpt-4o-mini",
                temperature=0.0,
                max_tokens=1024,
            )
        )
    )


def test_extract_response_values_expected_case():
    response = "2\t3\t1\treason"
    result = extract_response_values(response)
    assert result == (2, 3, 1, "reason", "")


def test_extract_response_values_invalid_values():
    response = "0\t1\t1\treason"
    result = extract_response_values(response)
    assert result[4]

    response = "1\t0\t1\treason"
    result = extract_response_values(response)
    assert result[4]

    response = "1\t2\t-1\treason"
    result = extract_response_values(response)
    assert result[4]

    response = "1\t3\t2\treason"
    result = extract_response_values(response)
    assert result[4]

    response = "3\t1\t2\treason"
    result = extract_response_values(response)
    assert result[4]

    response = "3\t1\t2\treason"
    result = extract_response_values(response)
    assert result[4]


def test_extract_response_values_non_int():
    response = "2\t2\tx\treason"
    result = answer_correctness.extract_response_values(response)
    assert result[4]


def test_extract_response_values_too_few_values():
    response = "2\t2\treason"
    result = answer_correctness.extract_response_values(response)
    # fewer than 4 values → error
    assert result[4]


def test_extract_response_values_too_many_values():
    response = "2\t2\t2\treason\textra"
    result = answer_correctness.extract_response_values(response)
    # only first 4 should be taken
    assert result == (2, 2, 2, "reason", "")


def test_evaluate_answers(monkeypatch, tmp_path):
    mock_prompt_content = "Prompt with {question} {reference_answer} {candidate_answer}"
    mock_input_content = "Question\tReference answer\tActual answer\nQ1\tRef\tAns\n"

    prompt_file_path = "prompt_file_path"
    in_file_path = "in_file_path"
    out_file_path = tmp_path / "out_file_name"

    # Mock open()
    real_open = builtins.open

    def mock_open(path, *args, **kwargs):
        if path == prompt_file_path:
            return io.StringIO(mock_prompt_content)
        elif path == in_file_path:
            return io.StringIO(mock_input_content)
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", mock_open)

    # Mock call_llm() and tqdm()
    answer_corectness_evaluator = AnswerCorrectnessEvaluator(llm=MagicMock())
    monkeypatch.setattr(answer_corectness_evaluator, "_generate", lambda *_: "2\t2\t2\treason")
    monkeypatch.setattr(answer_correctness, "tqdm", lambda x: x)

    # Run
    answer_correctness.evaluate_and_write(
        in_file_path,
        out_file_path,
        config=get_llm_config()
    )

    # Verify output file content
    written = out_file_path.read_text().splitlines()
    assert written[0].split("\t") == answer_correctness.OUT_FIELDS
    assert written[1].split("\t") == ["2", "2", "2", "reason", ""]
