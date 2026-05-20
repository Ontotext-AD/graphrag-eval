import pytest
import yaml

from graphrag_eval import llm_factory
from graphrag_eval.evaluation import Config
from graphrag_eval.steps.retrieval_answer import Evaluator


@pytest.mark.asyncio
async def test_retrieval_answer():
    path = "tests-with-llm/test_data/config-openai.yaml"
    with open(path, encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)
    config = Config(**config_dict)
    ragas_llm = llm_factory.create_llm(config)

    evaluator = Evaluator(ragas_llm)
    result = await evaluator.get_retrieval_evaluation_dict(
        question_text="Why is the sky blue?",
        reference_answer="Because of Rayleigh scattering.",
        actual_contexts=[
            {
                "id": "http://example.com/resource/doc/1",
                "text": "Rayleigh discovered that shorter wavelengths are scattered more than "
                        "long wavelengths."
            },
            {
                "id": "http://example.com/resource/doc/2",
                "text": "Gases scatter sunlight"
            }
        ],
    )
    assert isinstance(result["retrieval_answer_recall"], float)
    assert isinstance(result["retrieval_answer_precision"], float)
    assert isinstance(result["retrieval_answer_f1"], float)
    assert 0 <= result["retrieval_answer_recall"] <= 1
    assert 0 <= result["retrieval_answer_precision"] <= 1
    assert 0 <= result["retrieval_answer_f1"] <= 1
