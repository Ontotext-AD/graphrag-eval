from pathlib import Path

from .steps.evaluation import evaluate_steps


def run_evaluation(
        qa_dataset: list[dict],
        responses_dict: dict,
        custom_eval_config_file_path: str | Path | None = None,
) -> list[dict]:
    # Output metrics are not nested, for simpler aggregation
    answer_correctness_evaluator = None
    evaluation_results = []
    custom_evaluators = []
    if custom_eval_config_file_path:
        from .custom_evaluation import parse_config
        custom_evaluators = parse_config(custom_eval_config_file_path)
    for template in qa_dataset:
        template_id = template["template_id"]
        for question in template["questions"]:
            actual_result = responses_dict[question["id"]]
            eval_result = {
                "template_id": template_id,
                "question_id": actual_result["question_id"],
                "question_text": question["question_text"]
            }
            if "reference_answer" in question:
                eval_result["reference_answer"] = question["reference_answer"]
            if "reference_steps" in question:
                eval_result["reference_steps"] = question["reference_steps"]
            if "error" in actual_result:
                eval_result.update({
                    "status": "error",
                    "error": actual_result["error"],
                })
            else:
                eval_result["status"] = "success"

            if "actual_answer" in actual_result:
                eval_result["actual_answer"] = actual_result["actual_answer"]
                from graphrag_eval import answer_relevance
                eval_result.update(
                    answer_relevance.get_relevance_dict(
                        question["question_text"],
                        actual_result["actual_answer"],
                    )
                )

                if "reference_answer" in question:
                    from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator
                    if not answer_correctness_evaluator:
                        answer_correctness_evaluator = AnswerCorrectnessEvaluator()
                    eval_result.update(
                        answer_correctness_evaluator.get_correctness_dict(
                            question,
                            actual_result,
                        )
                    )
            eval_result.update(
                evaluate_steps(question, actual_result)
            )
            for evaluator in custom_evaluators:
                custom_metrics = evaluator.evaluate(question, actual_result)
                eval_result.update(**custom_metrics)
            for key in "input_tokens", "output_tokens", "total_tokens", "elapsed_sec":
                if key in actual_result:
                    eval_result[key] = actual_result[key]

            evaluation_results.append(eval_result)
    return evaluation_results
