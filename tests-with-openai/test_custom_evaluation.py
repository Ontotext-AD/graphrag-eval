from pathlib import Path

import yaml
from copy import deepcopy
from langevals_ragas.lib.common import RagasResult, Money
from pytest import raises

from graphrag_eval import (
    answer_correctness,
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
from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator
from graphrag_eval.custom_evaluation import CustomEvaluator
from tests.util import read_responses


DATA_DIR = Path(__file__).parent / "test_data"


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
        answer_correctness,
        "OpenAI",
        lambda: None
    )
    monkeypatch.setattr(
        AnswerCorrectnessEvaluator,
        "call_llm",
        lambda *_: "2\t2\t2\tanswer correctness reason"
    )
    monkeypatch.setattr(
        custom_evaluation,
        "OpenAI",
        lambda: None
    )


def test_run_custom_evaluation_ok(monkeypatch):
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
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
    actual_responses = read_responses(DATA_DIR / "actual_responses_1.jsonl")
    custom_eval_config_file_path = DATA_DIR / "custom_eval_config.yaml"
    evaluation_results = run_evaluation(
        reference_data, 
        actual_responses, 
        custom_eval_config_file_path
    )
    for i in range(3):
        with open(DATA_DIR / f"custom_eval_prompt_{i + 1}.md") as f:
            assert captured_prompts[i].strip() == f.read().strip()
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_4.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    aggregates = compute_aggregates(
        evaluation_results,
        custom_eval_config_file_path
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
    custom_eval_config_file_path = DATA_DIR / "custom_eval_config.yaml"
    with open(custom_eval_config_file_path, encoding="utf-8") as f:
        correct_config = yaml.safe_load(f)
    
    error_configs = [{}, [[]]]    
    for key in ["name", "inputs", "instructions", "outputs"]:
        error_config = deepcopy(correct_config)
        del error_config[0][key]
        error_configs.append(error_config)
    
    error_config = deepcopy(correct_config)
    error_config[1]["reference_steps"] = {}
    error_configs.append(error_config)
    
    error_config = deepcopy(correct_config)
    error_config[1]["actual_steps"] = {}
    error_configs.append(error_config)

    for k1 in "steps_name", "steps_keys":
        for k2 in "reference_steps", "actual_steps":
            error_config = deepcopy(correct_config)
            c = error_config[1]
            del c[k1]
            del c["inputs"][c["inputs"].index(k2)]
            error_configs.append(error_config)
    
    error_config = deepcopy(correct_config)
    c = error_config[1]
    c["steps_keys"].append("invalid")
    error_configs.append(error_config)

    for config in error_configs:
        monkeypatch.setattr(yaml, "safe_load", lambda _: config)
        with raises(custom_evaluation.ConfigError):
            run_evaluation(
                reference_data, 
                actual_responses, 
                custom_eval_config_file_path
            )


def test_run_custom_evaluation_llm_output_error(monkeypatch):
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    _mock_common_calls(monkeypatch)
    monkeypatch.setattr(CustomEvaluator, "call_llm", lambda *_: "hello")
    actual_responses = read_responses(DATA_DIR / "actual_responses_1.jsonl")
    custom_eval_config_file_path = DATA_DIR / "custom_eval_config.yaml"
    evaluation_results = run_evaluation(
        reference_data, 
        actual_responses, 
        custom_eval_config_file_path
    )
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_5.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    aggregates = compute_aggregates(
        evaluation_results,
        custom_eval_config_file_path
    )
    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_1.yaml").read_text(encoding="utf-8")
    )
    assert expected_aggregates == aggregates
    

def test_run_custom_evaluation_missing_reference_steps(monkeypatch):
    reference_data = yaml.safe_load(
        (DATA_DIR / "reference_1.yaml").read_text(encoding="utf-8")
    )
    _mock_common_calls(monkeypatch)
    actual_responses = read_responses(DATA_DIR / "actual_responses_1.jsonl")
    del reference_data[0]["questions"][0]["reference_steps"]
    del actual_responses["c10bbc8dce98a4b8832d125134a16153"]["actual_steps"]
    del actual_responses["c10bbc8dce98a4b8832d125134a16153"]["actual_answer"]
    custom_eval_config_file_path = DATA_DIR / "custom_eval_config.yaml"
    evaluation_results = run_evaluation(
        reference_data, 
        actual_responses, 
        custom_eval_config_file_path
    )
    expected_evaluation_results = yaml.safe_load(
        (DATA_DIR / "evaluation_6.yaml").read_text(encoding="utf-8")
    )
    assert expected_evaluation_results == evaluation_results
    aggregates = compute_aggregates(
        evaluation_results,
        custom_eval_config_file_path
    )
    expected_aggregates = yaml.safe_load(
        (DATA_DIR / "evaluation_summary_6.yaml").read_text(encoding="utf-8")
    )
    assert expected_aggregates == aggregates
