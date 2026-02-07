from copy import deepcopy
from pathlib import Path

import yaml
from langevals_ragas.lib.common import RagasResult, Money
from pytest import raises

from graphrag_eval import (
    compute_aggregates,
    custom_evaluation,
    run_evaluation,
)
from graphrag_eval.steps.retrieval_answer import (
    RagasResponseContextRecallEvaluator,
    RagasResponseContextPrecisionEvaluator,
)
from graphrag_eval.steps.retrieval_context_texts import (
    RagasContextPrecisionEvaluator,
    RagasContextRecallEvaluator,
)
from graphrag_eval.answer_relevance import RagasResponseRelevancyEvaluator
from graphrag_eval.custom_evaluation import CustomEvaluator
from tests.util import read_responses
from graphrag_eval import llm


DATA_DIR = Path(__file__).parent / "test_data"
CONFIG_FILE_PATH = DATA_DIR / "config-llm-and-custom-evaluations.yaml"


def _mock_common_calls(monkeypatch):
    monkeypatch.setattr(
        RagasResponseRelevancyEvaluator,
        'evaluate',
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="answer relevance reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        RagasResponseContextRecallEvaluator,
        "evaluate",
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="retrieval answer recall reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        RagasResponseContextPrecisionEvaluator,
        "evaluate",
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="retrieval answer precision reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        RagasContextRecallEvaluator,
        "evaluate",
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="retrieval context recall reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        RagasContextPrecisionEvaluator,
        "evaluate",
        lambda *_: RagasResult(
            status="processed",
            score=0.9,
            details="retrieval context precision reason",
            cost=Money(currency="USD", amount=0.0007)
        )
    )
    monkeypatch.setattr(
        llm,
        "call",
        lambda *_: "2\t2\t2\tanswer correctness reason"
    )


def test_run_custom_evaluation_ok(monkeypatch):
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    actual_responses = read_responses(DATA_DIR / "actual_responses_1.jsonl")
    _mock_common_calls(monkeypatch)
    captured_prompts = []
    i = 0
    def mock_call_llm(self, prompt):
        captured_prompts.append(prompt)
        nonlocal i
        i += 1
        if i == 1:
            return "0.9\tThe answer contains relevant information except for "\
                "the sentence about total revenue"
        if i == 2:
            return "0.5\t0.67\tThere are 4 reference claims and 3 actual "\
                "claims; 2 claims match"
        if i == 3:
            return "0.75\t0.6\tThe reference answer has 4 claims; there are 5 "\
                "SPARQL results; 3 claims match"
    monkeypatch.setattr(CustomEvaluator, "call_llm", mock_call_llm)
    evaluation_results = run_evaluation(
        reference_data,
        actual_responses,
        CONFIG_FILE_PATH,
    )
    for i in range(3):
        with open(DATA_DIR / f"custom_eval_prompt_{i + 1}.txt") as f:
            assert captured_prompts[i].strip() == f.read().strip()
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_4.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    aggregates = compute_aggregates(
        evaluation_results,
        CONFIG_FILE_PATH,
    )
    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_4.yaml").read_text(encoding="utf-8")
    )
    assert expected_aggregates == aggregates


def test_run_custom_evaluation_config_error(monkeypatch):
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    actual_responses = read_responses(DATA_DIR / "actual_responses_1.jsonl")
    with open(CONFIG_FILE_PATH, encoding="utf-8") as f:
        correct_config = yaml.safe_load(f)
    
    error_configs = []

    error_config = deepcopy(correct_config)
    del error_config['llm']
    error_configs.append(error_config)

    for custom_evals_configs in [], {}, [[]]:
        error_config = deepcopy(correct_config)
        error_config['custom_evaluations'] = custom_evals_configs
        error_configs.append(error_config)

    for key in ["name", "inputs", "instructions", "outputs"]:
        error_config = deepcopy(correct_config)
        del error_config['custom_evaluations'][0][key]
        error_configs.append(error_config)
    
    error_config = deepcopy(correct_config)
    error_config['custom_evaluations'][0]["extra"] = "invalid"
    error_configs.append(error_config)
    
    for k1 in "steps_name", "steps_keys":
        # custom_evaluations[1] has "reference_steps" and "actual_steps"
        for k2 in "reference_steps", "actual_steps":
            error_config = deepcopy(correct_config)
            c = error_config['custom_evaluations'][1]
            del c[k1]
            del c["inputs"][c["inputs"].index(k2)]
            error_configs.append(error_config)
    
    error_config = deepcopy(correct_config)
    c = error_config['custom_evaluations'][1]
    c["steps_keys"].append("invalid")
    error_configs.append(error_config)

    for key in custom_evaluation.RESERVED_KEYS:
        error_config = deepcopy(correct_config)
        error_config['custom_evaluations'][0]["outputs"][key] = "invalid"
        error_configs.append(error_config)

    for config in error_configs:
        monkeypatch.setattr(yaml, "safe_load", lambda _: config)
        with raises(ValueError):
            run_evaluation(
                reference_data,
                actual_responses,
                CONFIG_FILE_PATH,
            )


def test_run_custom_evaluation_llm_output_error(monkeypatch):
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    actual_responses = read_responses(DATA_DIR / "actual_responses_1.jsonl")
    _mock_common_calls(monkeypatch)
    monkeypatch.setattr(CustomEvaluator, "call_llm", lambda *_: "hello")
    evaluation_results = run_evaluation(
        reference_data,
        actual_responses,
        CONFIG_FILE_PATH,
    )
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_5.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    aggregates = compute_aggregates(
        evaluation_results,
        CONFIG_FILE_PATH,
    )
    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_1.yaml").read_text(encoding="utf-8")
    )
    assert expected_aggregates == aggregates
    

def test_run_custom_evaluation_missing_input_fields(monkeypatch):
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    actual_responses = read_responses(DATA_DIR / "actual_responses_1.jsonl")
    del reference_data[0]["questions"][0]["reference_steps"]
    del actual_responses["c10bbc8dce98a4b8832d125134a16153"]["actual_steps"]
    del actual_responses["c10bbc8dce98a4b8832d125134a16153"]["actual_answer"]
    _mock_common_calls(monkeypatch)
    evaluation_results = run_evaluation(
        reference_data,
        actual_responses,
        CONFIG_FILE_PATH,
    )
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_6.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    aggregates = compute_aggregates(
        evaluation_results,
        CONFIG_FILE_PATH,
    )
    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_6.yaml").read_text(encoding="utf-8")
    )
    assert expected_aggregates == aggregates
