from __future__ import annotations

from pathlib import Path
from typing import Self, TYPE_CHECKING

import yaml
from pydantic import BaseModel, Field, model_validator

from .answer_correctness import (
    AnswerCorrectnessConfig,
    AnswerCorrectnessEvaluator,
)
from .answer_relevance import AnswerRelevanceConfig, AnswerRelevanceEvaluator
from .custom_evaluation import EvaluatorConfig, CustomEvaluator
from .evaluator import Evaluator
from .llm_factory import LLMConfig, create_llm, create_embedder
from .steps.evaluation import evaluate_steps

if TYPE_CHECKING:
    from ragas.llms.base import InstructorBaseRagasLLM
    from ragas.embeddings.base import BaseRagasEmbeddings, BaseRagasEmbedding


class Config(BaseModel):
    llm: LLMConfig | None = None
    custom_evaluations: list[EvaluatorConfig] | None = Field(
        default=None,
        min_length=1
    )
    answer_correctness: AnswerCorrectnessConfig | None = None
    answer_relevance: AnswerRelevanceConfig | None = None

    @model_validator(mode="after")
    def validate_config_and_set_defaults(self) -> Self:
        has_llm = self.llm is not None
        has_embedding = has_llm and self.llm.embedding is not None

        if self.answer_correctness is None and has_llm:
            self.answer_correctness = AnswerCorrectnessConfig()

        if self.answer_relevance is None and has_embedding:
            self.answer_relevance = AnswerRelevanceConfig()

        if self.custom_evaluations and not has_llm:
            raise ValueError(
                "llm config is required if custom_evaluations are provided"
            )
        if (
            self.answer_correctness
            and self.answer_correctness.enabled
            and not has_llm
        ):
            raise ValueError(
                "llm config is required if answer correctness is enabled"
            )
        if (
            self.answer_relevance
            and self.answer_relevance.enabled
            and not has_embedding
        ):
            raise ValueError(
                "llm config including embedding is required if answer "
                "relevance is enabled"
            )
        return self

    @classmethod
    def parse(cls, config_file_path: str | Path | None) -> Self:
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
    evaluators, ragas_llm = parse_config_and_init_evaluators(config_file_path)

    # Output metrics are not nested, for simpler aggregation
    evaluation_results = []
    for template in qa_dataset:
        template_id = template["template_id"]
        for question in template["questions"]:
            actual_result = responses_dict[question["id"]]
            eval_result = {
                "template_id": template_id,
                "question_id": actual_result["question_id"],
                "question_text": question["question_text"]
            }
            for key in ("input_tokens", "output_tokens", "total_tokens",
                        "elapsed_sec"):
                if key in actual_result:
                    eval_result[key] = actual_result[key]
            if "actual_answer" in actual_result:
                eval_result["actual_answer"] = actual_result["actual_answer"]
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

            eval_result.update(
                await evaluate_steps(question, actual_result, ragas_llm)
            )
            for evaluator in evaluators:
                eval_result.update(
                    await evaluator.evaluate(question, actual_result)
                )

            evaluation_results.append(eval_result)
    return evaluation_results


def parse_config_and_init_evaluators(
    config_file_path: str | Path | None
) -> tuple[
    list[Evaluator],
    InstructorBaseRagasLLM | None,
]:
    config = Config.parse(config_file_path)
    ragas_llm: InstructorBaseRagasLLM | None = create_llm(config.llm)
    ragas_embedder: BaseRagasEmbeddings | BaseRagasEmbedding | None = (
        create_embedder(config.llm)
    )

    evaluators: list[Evaluator] = []

    answer_relevance_evaluator = AnswerRelevanceEvaluator.from_config(
        ragas_llm, ragas_embedder, config.answer_relevance
    )
    if answer_relevance_evaluator:
        evaluators.append(answer_relevance_evaluator)

    answer_correctness_evaluator = AnswerCorrectnessEvaluator.from_config(
        ragas_llm, config.answer_correctness
    )
    if answer_correctness_evaluator:
        evaluators.append(answer_correctness_evaluator)

    evaluators.extend(
        CustomEvaluator.from_config(ragas_llm, config.custom_evaluations)
    )

    return evaluators, ragas_llm
