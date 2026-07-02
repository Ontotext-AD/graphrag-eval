import pytest
import yaml

from graphrag_eval import llm_factory
from graphrag_eval.answer_relevance import AnswerRelevanceEvaluator
from graphrag_eval.evaluation import Config


@pytest.mark.asyncio
async def test_answer_relevance():
    path = "tests-with-llm/test_data/config-openai.yaml"
    with open(path, encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)
    config = Config(**config_dict)
    ragas_llm = llm_factory.create_llm(config.llm)
    ragas_embedder = llm_factory.create_embedder(config.llm)

    evaluator = AnswerRelevanceEvaluator(ragas_llm, ragas_embedder)
    result = await evaluator.evaluate(
        {"question_text": "Why is the sky blue?"},
        {"actual_answer": "Oxygen makes it blue"},
    )
    assert isinstance(result["answer_relevance"], float)
    assert 0 <= result["answer_relevance"] <= 1
