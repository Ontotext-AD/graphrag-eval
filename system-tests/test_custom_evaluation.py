import pytest

from graphrag_eval.evaluation import run_evaluation


@pytest.mark.asyncio
async def test_custom_evaluation():
    evaluation_results = await run_evaluation(
        [
            {
                "template_id": "template_1",
                "questions": [
                    {
                        "id": "question_1",
                        "question_text": "Ist ein Ledergürtel ein gefährliches Werkzeug?",
                        "reference_answer": "Ja"
                    }
                ]
            }
        ],
        {
            "question_1": {
                "question_id": "question_1",
                "actual_answer": "Nein"
            }
        },
        "system-tests/config/legal-config.yaml",
    )
    assert len(evaluation_results) == 1
    assert "legal_recall" in evaluation_results[0]
    assert "legal_precision" in evaluation_results[0]
    assert "legal_f1" in evaluation_results[0]
    assert "legal_reason" in evaluation_results[0]
