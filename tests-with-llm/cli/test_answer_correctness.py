import builtins
import io
from unittest.mock import MagicMock

import pytest

from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator
from graphrag_eval.cli import answer_correctness


@pytest.mark.asyncio
async def test_evaluate_answers(monkeypatch, tmp_path):
    mock_prompt_content = "Prompt with {question} {reference_answer} {actual_answer}"
    mock_input_content = "Question\tReference answer\tActual answer\nQ1\tRef\tAns\n"

    prompt_file_path = "prompt_file_path"
    in_file_path = "in_file_path"
    out_file_path = tmp_path / "out_file_name"

    # Mock open()
    real_open = builtins.open

    def mock_open(path, *args, **kwargs):
        str_path = str(path)
        if str_path == prompt_file_path:
            return io.StringIO(mock_prompt_content)
        elif str_path == in_file_path:
            return io.StringIO(mock_input_content)
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", mock_open)
    answer_correctness_evaluator = AnswerCorrectnessEvaluator(llm=MagicMock()).__class__

    async def mock_agenerate(self, prompt):
        return "2\t2\t2\treason"

    monkeypatch.setattr(
        answer_correctness_evaluator,
        "_agenerate",
        mock_agenerate
    )
    monkeypatch.setattr(answer_correctness, "tqdm", lambda x: x)

    # Run
    await answer_correctness.evaluate_and_write(
        in_file_path,
        out_file_path,
        evaluator=AnswerCorrectnessEvaluator(llm=MagicMock())
    )

    # Verify output file content
    written = out_file_path.read_text().splitlines()
    assert written[0].split("\t") == ["#Reference", "#PTarget", "#Matching", "Reasoning", "Error"]
    assert written[1].split("\t") == ["2", "2", "2", "reason", ""]
