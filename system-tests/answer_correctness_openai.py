import yaml

from graphrag_eval import llm
from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator
from graphrag_eval.evaluation import Config


config_path = "tests-with-llm/test_data/config-openai.yaml"
with open(config_path, encoding="utf-8") as f:
    config_dict = yaml.safe_load(f)
config = Config(**config_dict)
ragas_llm = llm.create_llm(config)
ragas_embedder = llm.create_embedder(config)


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

def test_answer_correctness():
    evaluator = AnswerCorrectnessEvaluator(llm=ragas_llm)
    result = evaluator.get_correctness_dict(reference, actual)
    assert isinstance(result["answer_recall"], float)
    assert isinstance(result["answer_precision"], float)
    assert isinstance(result["answer_f1"], float)
    assert 0.0 <= result["answer_recall"] <= 1.0
    assert 0.0 <= result["answer_precision"] <= 1.0
    assert 0.0 <= result["answer_f1"] <= 1.0
