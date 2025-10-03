from pathlib import Path

import yaml

from graphrag_eval import compute_aggregates

DATA_DIR = Path(__file__).parent / "test_data"


def test_compute_aggregates_doesnt_throw_exception():
    # The issue was that the actual SPARQL query is a DESCRIBE query containing the string "results" in the text.
    evaluation_results_file = DATA_DIR / f"evaluation_3.yaml"
    with open(evaluation_results_file, "r", encoding="utf-8") as yaml_file:
        per_question_eval = yaml.safe_load(yaml_file)
        compute_aggregates(per_question_eval)
