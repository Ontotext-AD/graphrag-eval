import pytest
import yaml

from graphrag_eval.evaluation import Config
from graphrag_eval.answer_relevance import get_relevance_dict


path = "tests-with-llm/test_data/config-llm.yaml"
with open(path, encoding="utf-8") as f:
    config_dict = yaml.safe_load(f)
config = Config(**config_dict)


@pytest.mark.asyncio
async def test_answer_relevance():
    result = await get_relevance_dict(
        question_text="Why is the sky blue?",
        actual_answer="Oxygen makes it blue",
        llm_config=config.llm,
    )
    result = get_relevance_dict(
        question_text="Why is the sky blue?",
        actual_answer="Oxygen makes it blue",
        llm_config=config.llm,
    )
    assert isinstance(result["answer_relevance"], float)
    assert 0 <= result["answer_relevance"] <= 1
