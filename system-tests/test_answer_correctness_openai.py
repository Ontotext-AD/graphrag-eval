import pytest
import yaml

from graphrag_eval import llm_factory
from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator
from graphrag_eval.evaluation import Config


@pytest.mark.asyncio
async def test_answer_correctness():
    config_path = "tests-with-llm/test_data/config-openai.yaml"
    with open(config_path, encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)
    config = Config(**config_dict)
    ragas_llm = llm_factory.create_llm(config.llm)

    reference = {
        "template_id": "geography",
        "question_id": "bulgaria",
        "question_text": "What is the capital of Bulgaria?",
        "reference_answer": "Sofia",
    }
    actual = {
        "question_id": "bulgaria",
        "actual_answer": "The capital of Bulgaria is Sofia"
    }

    evaluator = AnswerCorrectnessEvaluator(ragas_llm=ragas_llm)
    result = await evaluator.evaluate(reference, actual)
    assert isinstance(result["answer_recall"], float)
    assert isinstance(result["answer_precision"], float)
    assert isinstance(result["answer_f1"], float)
    assert 0.0 <= result["answer_recall"] <= 1.0
    assert 0.0 <= result["answer_precision"] <= 1.0
    assert 0.0 <= result["answer_f1"] <= 1.0
