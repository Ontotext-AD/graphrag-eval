from pathlib import Path

import yaml
from pydantic import BaseModel, Field, model_validator

from . import custom_evaluation
from .llm import Config as LLMConfig, create_llm, create_embedder
from .steps.evaluation import evaluate_steps


class Config(BaseModel):
    llm: LLMConfig | None = None
    custom_evaluations: list[custom_evaluation.Config] | None \
        = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_config(self) -> "Config":
        if self.custom_evaluations and not self.llm:
            msg = "llm config is required if custom_evaluations are provided"
            raise ValueError(msg)
        return self
    
    @classmethod
    def parse(cls, config_file_path: str | Path | None) -> "Config":
        if config_file_path:
            with open(config_file_path, encoding="utf-8") as f:
                config_dict = yaml.safe_load(f)
            return cls(**config_dict)
        return cls()


async def run_evaluation(
    qa_dataset: list[dict],
    responses_dict: dict,
    config_file_path: str | Path | None = None,
) -> list[dict]:
    # Output metrics are not nested, for simpler aggregation
    evaluation_results = []
    config = Config.parse(config_file_path)
    ragas_llm = create_llm(config)
    ragas_embedder = create_embedder(config)
    custom_evaluators = custom_evaluation.create_evaluators(config)
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
                if ragas_llm:
                    from graphrag_eval.answer_relevance import Evaluator
                    relevance_evaluator = Evaluator(ragas_llm, ragas_embedder)
                    eval_result.update(
                        await relevance_evaluator.get_relevance_dict(
                            question["question_text"],
                            actual_result["actual_answer"],
                        )
                    )
                if "reference_answer" in question and ragas_llm:
                    from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator
                    answer_correctness_evaluator = AnswerCorrectnessEvaluator(
                        llm=ragas_llm
                    )
                    eval_result.update(
                        answer_correctness_evaluator.get_correctness_dict(
                            question,
                            actual_result,
                        )
                    )
            eval_result.update(
                await evaluate_steps(
                    question,
                    actual_result,
                    ragas_llm,
                )
            )
            for relevance_evaluator in custom_evaluators:
                custom_metrics = relevance_evaluator.evaluate(question, actual_result)
                eval_result.update(**custom_metrics)
            for key in "input_tokens", "output_tokens", "total_tokens", "elapsed_sec":
                if key in actual_result:
                    eval_result[key] = actual_result[key]

            evaluation_results.append(eval_result)
    return evaluation_results
