from pprint import pprint

from graphrag_eval.steps.retrieval_context_texts import (
    get_retrieval_evaluation_dict
)


result_dict = get_retrieval_evaluation_dict(
    reference_contexts=[
        {
            "id": "http://example.com/resource/doc/1",
            "text": "Rayleigh discovered that shorter wavelengths are scattered more than long wavelengths."
        },
        {
            "id": "http://example.com/resource/doc/2",
            "text": "Gases scatter sunlight"
        }
    ],
    actual_contexts=[
        {
            "id": "http://example.com/resource/doc/3",
            "text": "In Rayleigh scattering, shorter wavelengths are scattered more"
        },
        {
            "id": "http://example.com/resource/doc/4",
            "text": "The sun shines onto the atmosphere. The atmosphere contains various gases."
        }
    ]
)
pprint(result_dict)
assert isinstance(result_dict["retrieval_context_recall"], float)
assert isinstance(result_dict["retrieval_context_precision"], float)
assert isinstance(result_dict["retrieval_context_f1"], float)
assert 0 <= result_dict["retrieval_context_recall"] <= 1
assert 0 <= result_dict["retrieval_context_precision"] <= 1
assert 0 <= result_dict["retrieval_context_f1"] <= 1
