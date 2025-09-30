from pathlib import Path

import yaml

from graphrag_eval import (
    compute_aggregates,
    run_evaluation,
)
from graphrag_eval.aggregation import stats_for_series
from graphrag_eval.steps.evaluation import evaluate_steps
from .util import read_responses


DATA_DIR = Path(__file__).parent / "test_data"


def test_stats_for_series():
    assert stats_for_series([]) == {
        "sum": 0,
        "mean": 0,
        "median": 0,
        "min": 0,
        "max": 0,
    }
    assert stats_for_series([1]) == {
        "sum": 1,
        "mean": 1,
        "median": 1,
        "min": 1,
        "max": 1,
    }
    assert stats_for_series([1.5]) == {
        "sum": 1.5,
        "mean": 1.5,
        "median": 1.5,
        "min": 1.5,
        "max": 1.5,
    }
    assert stats_for_series([1, 2]) == {
        "sum": 3,
        "mean": 1.5,
        "median": 1.5,
        "min": 1,
        "max": 2,
    }
    assert stats_for_series([i for i in reversed(range(10))]) == {
        "sum": 45,
        "mean": 4.5,
        "median": 4.5,
        "min": 0,
        "max": 9,
    }


def test_run_evaluation_and_compute_aggregates():
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    responses_path = DATA_DIR / "actual_responses_1.jsonl"
    actual_responses = read_responses(responses_path)
    evaluation_results = run_evaluation(reference_data, actual_responses)
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_1.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert expected_evaluation_results == evaluation_results
    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_1.yaml").read_text(
            encoding="utf-8"
        )
    )
    aggregates = compute_aggregates(evaluation_results)
    assert expected_aggregates == aggregates


def test_run_evaluation_and_compute_aggregates_all_errors():
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    responses_path = DATA_DIR / "actual_responses_2.jsonl"
    actual_responses = read_responses(responses_path)
    evaluation_results = run_evaluation(reference_data, actual_responses)
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_2.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert expected_evaluation_results == evaluation_results
    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_2.yaml").read_text(
            encoding="utf-8"
        )
    )
    aggregates = compute_aggregates(evaluation_results)
    assert expected_aggregates == aggregates


def test_get_steps_matches():
    expected_steps = [
        [
            {"name": "step_a", "output": "result_a_1", "status": "success"},
            {"name": "step_a", "output": "result_a_2", "status": "success"},
        ],
        [
            {"name": "step_b", "output": "result_b_2", "status": "success"},
        ],
    ]
    actual_steps = [
        {"name": "step_a", "output": "result_a_1", "status": "success", "id": "1"},
        {"name": "step_b", "error": "error", "status": "error", "id": "2"},
        {"name": "step_b", "error": "error", "status": "error", "id": "3"},
        {"name": "step_a", "output": "result_a", "status": "success", "id": "4"},
        {"name": "step_b", "error": "error", "status": "error", "id": "5"},
    ]
    assert evaluate_steps(expected_steps, actual_steps) == 0
    assert "matches" not in expected_steps[-1][0]

    expected_steps = [
        [
            {"name": "step_a", "output": "result_a_1", "status": "success"},
            {"name": "step_a", "output": "result_a_2", "status": "success"},
        ],
        [
            {"name": "step_b", "output": "result_b_2", "status": "success"},
        ],
    ]
    actual_steps = [
        {"name": "step_a", "output": "result_a_1", "status": "success", "id": "1"},
        {"name": "step_a", "output": "result_a_2", "status": "success", "id": "2"},
        {"name": "step_b", "output": "result_b_2", "status": "success", "id": "3"},
        {"name": "step_b", "error": "error", "status": "error", "id": "4"},
        {"name": "step_a", "output": "result_a", "status": "success", "id": "5"},
        {"name": "step_b", "output": "result_b_1", "status": "success", "id": "6"},
    ]
    assert evaluate_steps(expected_steps, actual_steps) == 1
    assert expected_steps[-1][0]["matches"] == "3"

    expected_steps = [
        [
            {"name": "step_a", "output": "result_a_1", "status": "success"},
            {"name": "step_a", "output": "result_a_2", "status": "success"},
        ],
        [
            {"name": "step_b", "output": "result_b_1", "status": "success"},
            {"name": "step_b", "output": "result_b_2", "status": "success"},
        ],
    ]
    actual_steps = [
        {"name": "step_b", "output": "result_b_2", "status": "success", "id": "1"},
        {"name": "step_b", "error": "error", "status": "error", "id": "2"},
        {"name": "step_a", "output": "result_a", "status": "success", "id": "3"},
        {"name": "step_b", "output": "result_b_1", "status": "success", "id": "4"},
    ]
    assert evaluate_steps(expected_steps, actual_steps) == 1
    assert expected_steps[-1][0]["matches"] == "4"
    assert expected_steps[-1][1]["matches"] == "1"

    expected_steps = [
        [
            {"name": "step_a", "output": "result_a_1", "status": "success"},
            {"name": "step_a", "output": "result_a_2", "status": "success"},
        ],
        [
            {"name": "step_b", "output": "result_b_1", "status": "success"},
            {"name": "step_b", "output": "result_b_2", "status": "success"},
        ],
    ]
    actual_steps = [
        {"name": "step_b", "output": "result_b_24", "status": "success", "id": "1"},
        {"name": "step_b", "error": "error", "status": "error", "id": "2"},
        {"name": "step_a", "output": "result_a", "status": "success", "id": "3"},
        {"name": "step_b", "output": "result_b_1", "status": "success", "id": "4"},
    ]
    assert evaluate_steps(expected_steps, actual_steps) == 0.5
    assert expected_steps[-1][0]["matches"] == "4"
    assert "matches" not in expected_steps[-1][1]


def test_evaluate_steps_expected_select_actual_ask():
    expected_steps = yaml.safe_load(
        (DATA_DIR / "expected_steps_1.yaml").read_text(
            encoding="utf-8"
        )
    )
    actual_steps = yaml.safe_load(
        (DATA_DIR / "actual_steps_1.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert evaluate_steps(expected_steps, actual_steps) == 0
    assert "matches" not in expected_steps[-1][0]

    expected_steps = yaml.safe_load(
        (DATA_DIR / "expected_steps_2.yaml").read_text(
            encoding="utf-8"
        )
    )
    actual_steps = yaml.safe_load(
        (DATA_DIR / "actual_steps_2.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert evaluate_steps(expected_steps, actual_steps) == 0
    assert "matches" not in expected_steps[-1][0]


def test_evaluate_steps_expected_select_actual_describe():
    expected_steps = yaml.safe_load(
        (DATA_DIR / "expected_steps_3.yaml").read_text(
            encoding="utf-8"
        )
    )
    actual_steps = yaml.safe_load(
        (DATA_DIR / "actual_steps_3.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert evaluate_steps(expected_steps, actual_steps) == 0
    assert "matches" not in expected_steps[-1][0]


def test_evaluate_steps_expected_select_actual_ask_and_then_select():
    expected_steps = yaml.safe_load(
        (DATA_DIR / "expected_steps_4.yaml").read_text(
            encoding="utf-8"
        )
    )
    actual_steps = yaml.safe_load(
        (DATA_DIR / "actual_steps_4.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert evaluate_steps(expected_steps, actual_steps) == 1
    assert "matches" in expected_steps[-1][0]
    assert expected_steps[-1][0]["matches"] == "call_3qJK186HZj1twnr6x976slHN"
