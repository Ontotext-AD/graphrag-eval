from pathlib import Path

import yaml
from pydantic import BaseModel, Field, model_validator

from . import custom_evaluation
from . import llm as llm_
from .steps.evaluation import evaluate_steps


class Config(BaseModel):
    llm: llm_.Config | None = None
    custom_evaluations: list[custom_evaluation.Config] | None \
        = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_config(self):
        if self.custom_evaluations and not self.llm:
            msg = "llm config is required if custom_evaluations are provided"
            raise ValueError(msg)
        return self

def run_evaluation(
        qa_dataset: list[dict],
        responses_dict: dict,
        config_file_path: str | Path | None = None,
) -> list[dict]:
    # Output metrics are not nested, for simpler aggregation
    answer_correctness_evaluator = None
    evaluation_results = []
    custom_evaluators = []
    config = Config()
    if config_file_path:
        with open(config_file_path, encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)
        config = Config(**config_dict)
    if config.custom_evaluations and config.llm:
        from .custom_evaluation import CustomEvaluator
        custom_evaluators = [
            CustomEvaluator(c, config.llm)
            for c in config.custom_evaluations
        ]
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
                if config.llm:
                    from graphrag_eval import answer_relevance
                    eval_result.update(
                        answer_relevance.get_relevance_dict(
                            question["question_text"],
                            actual_result["actual_answer"],
                            llm_config=config.llm,
                        )
                    )

                if "reference_answer" in question and config.llm:
                    from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator
                    if not answer_correctness_evaluator:
                        answer_correctness_evaluator = AnswerCorrectnessEvaluator(
                            llm_config=config.llm
                        )
                    eval_result.update(
                        answer_correctness_evaluator.get_correctness_dict(
                            question,
                            actual_result,
                        )
                    )
            eval_result.update(
                evaluate_steps(question, actual_result, llm_config=config.llm)
            )
            for evaluator in custom_evaluators:
                custom_metrics = evaluator.evaluate(question, actual_result)
                eval_result.update(**custom_metrics)
            for key in "input_tokens", "output_tokens", "total_tokens", "elapsed_sec":
                if key in actual_result:
                    eval_result[key] = actual_result[key]

            evaluation_results.append(eval_result)
    return evaluation_results
