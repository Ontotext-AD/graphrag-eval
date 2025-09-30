from pprint import pprint

from graphrag_eval.answer_relevance import (
    get_relevance_dict
)


result = get_relevance_dict(
    question_text="Why is the sky blue?",
    actual_answer="Oxygen makes it blue"
)

pprint(result)
assert 0 <= result["answer_relevance"] <= 1
assert 0 <= result["answer_relevance_cost"]
assert isinstance(result["answer_relevance_reason"], str)
