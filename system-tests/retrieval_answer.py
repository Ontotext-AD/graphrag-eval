import pytest

from graphrag_eval.steps.retrieval_answer import get_retrieval_evaluation_dict


@pytest.mark.asyncio
async def test_retrieval_answer():
    result = await get_retrieval_evaluation_dict(
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

    assert isinstance(result["retrieval_answer_recall"], float)
    assert isinstance(result["retrieval_answer_precision"], float)
    assert isinstance(result["retrieval_answer_f1"], float)
    assert 0 <= result["retrieval_answer_recall"] <= 1
    assert 0 <= result["retrieval_answer_precision"] <= 1
    assert 0 <= result["retrieval_answer_f1"] <= 1
