from pprint import pprint

from graphrag_eval.steps.retrieval_answer import (
    get_retrieval_evaluation_dict
)


result_dict = get_retrieval_evaluation_dict(
    question_text="Why is the sky blue?",
    reference_answer="Because of Rayleigh scattering.",
    actual_contexts=[
        {
            "id": "http://example.com/resource/doc/1",
            "text": "Rayleigh discovered that shorter wavelengths are scattered more than long wavelengths."
        },
        {
            "id": "http://example.com/resource/doc/2",
            "text": "Gases scatter sunlight"
        }
    ]
)
pprint(result_dict)
assert 0 <= result_dict["retrieval_answer_recall"] <= 1
assert isinstance(result_dict["retrieval_answer_recall_reason"], str)
assert 0 <= result_dict["retrieval_answer_recall_cost"]
assert 0 <= result_dict["retrieval_answer_precision"] <= 1
assert 0 <= result_dict["retrieval_answer_precision_cost"]
assert 0 <= result_dict["retrieval_answer_f1"] <= 1
assert 0 <= result_dict["retrieval_answer_f1_cost"] == result_dict["retrieval_answer_recall_cost"] + result_dict["retrieval_answer_precision_cost"]
