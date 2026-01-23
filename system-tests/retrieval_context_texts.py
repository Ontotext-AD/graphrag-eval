import pytest

from graphrag_eval.steps.retrieval_context_texts import (
    get_retrieval_evaluation_dict
)


@pytest.mark.asyncio
async def test_retrieval_contexts():
    result = await get_retrieval_evaluation_dict(
        reference_answer="Rayleigh discovered that shorter wavelengths are scattered more than long wavelengths.",
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

    assert isinstance(result["retrieval_context_recall"], float)
    assert 0 <= result["retrieval_context_recall"] <= 1
