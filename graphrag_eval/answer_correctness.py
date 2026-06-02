from pathlib import Path

from pydantic import BaseModel, Field

from graphrag_eval.util import compute_f1, singleton


def load_default_prompt() -> str:
    with open(Path(__file__).parent / "prompts" / "template.md", "r", encoding="utf-8") as f:
        return f.read()


class AnswerCorrectnessConfig(BaseModel):
    prompt: str = Field(default_factory=load_default_prompt)


@singleton
class AnswerCorrectnessEvaluator:
    def __init__(
        self,
        llm: "InstructorBaseRagasLLM",
        config: AnswerCorrectnessConfig | None = None,
    ):
        self.config = config or AnswerCorrectnessConfig()
        self.prompt_template = self.config.prompt
        self.llm = llm

    async def _agenerate(self, prompt):
        """Wrapper method for easier testing"""
        return (await self.llm.agenerate(prompt, None)).choices[0].message.content

    async def evaluate_answer(
        self,
        question: str,
        reference_answer: str,
        actual_answer: str
    ) -> tuple[int, int, int, str]:
        if any(not s.strip() for s in [question, reference_answer, actual_answer]):
            raise ValueError("The question of the reference or the actual answer is a blank "
                             "string!")
        prompt = self.prompt_template.format(
            question=question,
            reference_answer=reference_answer,
            actual_answer=actual_answer,
        )
        response_str = await self._agenerate(prompt)
        return self.extract_response_values(response_str)

    async def get_correctness_dict(
        self,
        reference: dict,
        actual: dict,
    ):
        result = {"reference_answer": reference["reference_answer"]}
        try:
            num_ref_claims, num_actual_claims, num_matching_claims, reason = \
                await self.evaluate_answer(
                    reference["question_text"],
                    reference["reference_answer"],
                    actual["actual_answer"],
                )
            result.update({
                "answer_reference_claims_count": num_ref_claims,
                "answer_actual_claims_count": num_actual_claims,
                "answer_matching_claims_count": num_matching_claims,
                "answer_correctness_reason": reason,
            })
            recall, precision, f1 = self.compute_recall_precision_f1(
                num_ref_claims, num_actual_claims, num_matching_claims
            )
            if recall is not None:
                result["answer_recall"] = recall
            if precision is not None:
                result["answer_precision"] = precision
            if f1 is not None:
                result["answer_f1"] = f1
        except Exception as exc:
            result["answer_eval_error"] = str(exc)
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

    @staticmethod
    def extract_response_values(
        response: str
    ) -> tuple[int, int, int, str]:
        vals = response.split("\t")
        n = len(vals)
        if n < 4:
            raise ValueError(f"Expected 4 tab-separated values: {response}")
        vals = vals[:4]
        try:
            n_ref, n_actual, n_matching = map(int, vals[:3])
        except ValueError:
            raise ValueError(f"Claims counts should be ints: {vals}")
        if any([
            n_ref < 1,
            n_actual < 1,
            n_matching < 0,
            n_matching > n_ref,
            n_matching > n_actual
        ]):
            raise ValueError(
                f"Invalid claims counts combination: {n_ref}\t{n_actual}\t{n_matching}"
            )
        return n_ref, n_actual, n_matching, vals[3]
