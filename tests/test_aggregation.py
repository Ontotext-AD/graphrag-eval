from collections import defaultdict
from pathlib import Path

import pytest
import yaml

from graphrag_eval import compute_aggregates
from graphrag_eval.aggregation import (
    stats_for_series,
    update_step_metrics,
    update_steps_summary,
)

DATA_DIR = Path(__file__).parent / "test_data"


def test_compute_aggregates_doesnt_throw_exception():
    """
    Check that `compute_aggregates()` works when the actual SPARQL query 
    is a DESCRIBE query containing the string "results" in the text.
    """
    evaluation_results_file = DATA_DIR / f"evaluation_3.yaml"
    with open(evaluation_results_file, encoding="utf-8") as yaml_file:
        per_question_eval = yaml.safe_load(yaml_file)
        compute_aggregates(per_question_eval)


def test_compute_aggregates_doesnt_throw_type_error():
    """
    Check that `compute_aggregates()` works when the step output is an empty
    list.
    """
    evaluation_results_file = DATA_DIR / f"evaluation_7.yaml"
    with open(evaluation_results_file, encoding="utf-8") as yaml_file:
        per_question_eval = yaml.safe_load(yaml_file)
        compute_aggregates(per_question_eval)


def test_update_steps_summary_with_dict_output():
    """
    Check that `update_steps_summary()` properly handles pre-parsed dict step outputs
    and correctly increments empty_results when bindings are empty.
    """
    summary = {
        "total": defaultdict(int),
        "errors": defaultdict(int),
        "once_per_sample": defaultdict(int),
        "empty_results": defaultdict(int),
    }
    sample = {
        "actual_steps": [
            {
                "name": "sparql_query",
                "status": "success",
                "output": {"results": {"bindings": []}},
            },
            {
                "name": "sparql_query",
                "status": "success",
                "output": {"results": {"bindings": [{"uri": "http://example.org"}]}},
            },
            {
                "name": "sparql_query",
                "status": "error",
                "output": None,
            },
        ]
    }
    update_steps_summary(sample, summary)
    assert summary["total"]["sparql_query"] == 3
    assert summary["errors"]["sparql_query"] == 1
    assert summary["once_per_sample"]["sparql_query"] == 1
    assert summary["empty_results"]["sparql_query"] == 1


def test_update_step_metrics_and_stats():
    """
    Check that step metrics and summary stats are extracted properly.
    """
    step_metrics = defaultdict(list)
    sample = {
        "actual_steps": [
            {
                "name": "retrieval",
                "retrieval_answer_precision": 0.8,
                "retrieval_answer_recall": 1.0,
            }
        ]
    }
    update_step_metrics(sample, step_metrics)
    assert step_metrics["retrieval_answer_precision"] == [0.8]
    assert step_metrics["retrieval_answer_recall"] == [1.0]

    stats = stats_for_series([10, 20, 30])
    assert stats["sum"] == 60
    assert stats["mean"] == 20.0
    assert stats["min"] == 10
    assert stats["max"] == 30
