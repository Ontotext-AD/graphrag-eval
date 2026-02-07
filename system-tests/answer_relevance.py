import yaml
from pprint import pprint

from graphrag_eval.evaluation import Config
from graphrag_eval.answer_relevance import (
    get_relevance_dict
)


path = "tests-with-openai/test_data/config-llm.yaml"
with open(path, encoding="utf-8") as f:
    config_dict = yaml.safe_load(f)
config = Config(**config_dict)
result = get_relevance_dict(
    question_text="Why is the sky blue?",
    actual_answer="Oxygen makes it blue",
    llm_config=config.llm,
)

pprint(result)
assert isinstance(result["answer_relevance"], float)
assert 0 <= result["answer_relevance"] <= 1
assert 0 <= result["answer_relevance_cost"]
assert isinstance(result["answer_relevance_reason"], str)
