import os
import pytest
import yaml

from graphrag_eval.evaluation import Config
from graphrag_eval.answer_relevance import Evaluator
from graphrag_eval import llm


path = "tests-with-llm/test_data/config-azure.yaml"
with open(path, encoding="utf-8") as f:
    config_dict = yaml.safe_load(f)
# Hack to set different API keys without committing them
config_dict["llm"]["generation"]["api_key"] = os.getenv("AZURE_OPENAI_GENERATION_KEY")
config_dict["llm"]["embedding"]["api_key"] = os.getenv("AZURE_OPENAI_EMBEDDING_KEY")
config = Config(**config_dict)
ragas_llm = llm.create_llm(config)
ragas_embedder = llm.create_embedder(config)

@pytest.mark.asyncio
async def test_answer_relevance():
    evaluator = Evaluator(ragas_llm, ragas_embedder)
    result = await evaluator.get_relevance_dict(
        question_text="Why is the sky blue?",
        actual_answer="Oxygen makes it blue",
    )
    assert "answer_relevance_error" not in result
    assert "answer_relevance" in result
    assert isinstance(result["answer_relevance"], float)
    assert 0 <= result["answer_relevance"] <= 1
