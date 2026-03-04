import pytest
import yaml

from graphrag_eval.evaluation import Config
from graphrag_eval.answer_relevance import Evaluator
from graphrag_eval import llm


path = "tests-with-llm/test_data/config-llm.yaml"
with open(path, encoding="utf-8") as f:
    config_dict = yaml.safe_load(f)
config = Config(**config_dict)
ragas_llm, ragas_embedder = llm.create_llm_and_embedder(config)


@pytest.mark.asyncio
async def test_answer_relevance():
    evaluator = Evaluator(ragas_llm, ragas_embedder)
    result = await evaluator.get_relevance_dict(
        question_text="Why is the sky blue?",
        actual_answer="Oxygen makes it blue",
    )
    assert isinstance(result["answer_relevance"], float)
    assert 0 <= result["answer_relevance"] <= 1
