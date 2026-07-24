from __future__ import annotations

from pathlib import Path
from typing import Any, Self, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, model_validator

from graphrag_eval.util import compute_f1
from .evaluator import Evaluator

if TYPE_CHECKING:
    from ragas.llms.base import InstructorBaseRagasLLM


def load_default_prompt() -> str:
    with open(
        Path(__file__).parent / "prompts" / "template.md",
        encoding="utf-8"
    ) as f:
        return f.read()


class AnswerCorrectnessConfig(BaseModel):
    enabled: bool = Field(default=True)
    prompt: str = Field(default_factory=load_default_prompt)


class AnswerCorrectnessResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reference_claims_count: int = Field(ge=1)
    actual_claims_count: int = Field(ge=1)
    matching_claims_count: int = Field(ge=0)
    reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_claim_counts(self) -> "AnswerCorrectnessResult":
        if (
            self.matching_claims_count > self.reference_claims_count or
            self.matching_claims_count > self.actual_claims_count
        ):
            raise ValueError(
                "matching_claims_count must be less than or equal to both "
                "reference_claims_count and actual_claims_count"
            )
        return self


class InvalidPromptException(Exception):
    def __init__(
        self,
        message="The prompt template is invalid and cannot be "
                "formatted."
    ):
        self.message = message
        super().__init__(self.message)


class AnswerCorrectnessEvaluator:
    def __init__(
        self,
        ragas_llm: InstructorBaseRagasLLM,
        config: AnswerCorrectnessConfig | None = None,
    ):
        self.config = config or AnswerCorrectnessConfig()
        self.__validate_prompt_template(self.config.prompt)
        self.prompt_template = self.config.prompt
        self.ragas_llm = ragas_llm

    @classmethod
    def from_config(
        cls,
        ragas_llm: InstructorBaseRagasLLM | None,
        config: AnswerCorrectnessConfig | None
    ) -> Self | None:
        if ragas_llm is None:
            return None
        if config is None or not config.enabled:
            return None
        return cls(ragas_llm=ragas_llm, config=config)

    @staticmethod
    def __validate_prompt_template(prompt_template: str):
        try:
            prompt_template.format(
                question="Q?",
                reference_answer="R",
                actual_answer="A",
            )
        except Exception as exc:
            raise InvalidPromptException(
                "Invalid prompt template. Must only contain placeholders: "
                "{question}, {reference_answer}, and {actual_answer}. "
                f"Original error: {exc}"
            ) from exc

    async def _agenerate(self, prompt: str) -> AnswerCorrectnessResult:
        """Wrapper method for easier testing"""
        response = await self.ragas_llm.agenerate(prompt, AnswerCorrectnessResult)
        return AnswerCorrectnessResult.model_validate(response)

    async def evaluate_answer(
        self,
        question: str,
        reference_answer: str,
        actual_answer: str
    ) -> AnswerCorrectnessResult:
        if any(
            not s.strip() for s in [question, reference_answer, actual_answer]
        ):
            raise ValueError(
                "The question of the reference or the actual answer is a blank "
                "string!"
            )
        prompt = self.prompt_template.format(
            question=question,
            reference_answer=reference_answer,
            actual_answer=actual_answer,
        )
        return await self._agenerate(prompt)

    async def evaluate(
        self,
        reference: dict[str, Any],
        actual: dict[str, Any]
    ) -> dict[str, Any]:
        if "actual_answer" not in actual or "reference_answer" not in reference:
            return {}
        result = {}
        try:
            correctness = await self.evaluate_answer(
                reference["question_text"],
                reference["reference_answer"],
                actual["actual_answer"],
            )
            result.update({
                "answer_reference_claims_count": correctness.reference_claims_count,
                "answer_actual_claims_count": correctness.actual_claims_count,
                "answer_matching_claims_count": correctness.matching_claims_count,
                "answer_correctness_reason": correctness.reason,
            })
            recall, precision, f1 = self.compute_recall_precision_f1(
                correctness.reference_claims_count,
                correctness.actual_claims_count,
                correctness.matching_claims_count,
            )
            if recall is not None:
                result["answer_recall"] = recall
            if precision is not None:
                result["answer_precision"] = precision
            if f1 is not None:
                result["answer_f1"] = f1
        except Exception as exc:
            result["answer_correctness_error"] = str(exc)
        return result

    @staticmethod
    def compute_recall_precision_f1(
        n_pos: int,
        n_pred_pos: int,
        n_true_pos: int,
    ) -> tuple[float | None, float | None, float | None]:
        recall = None
        precision = None
        if n_pos:
            recall = n_true_pos / n_pos
        if n_pred_pos:
            precision = n_true_pos / n_pred_pos
        return recall, precision, compute_f1(recall, precision)


_: Evaluator = AnswerCorrectnessEvaluator
