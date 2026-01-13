from pathlib import Path

from openai import OpenAI


LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.0


class CustomEvaluator:
    def __init__(
        self, instructions_file_path: str,
        temperature : float = TEMPERATURE
    ):
        self.prompt_template = open(instructions_file_path).read()
        self.metric_name = Path(instructions_file_path).stem
        self.openai_client = OpenAI()
        self.temperature = temperature

    def call_llm(self, prompt: str) -> str:
        try:
            response = self.openai_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature
            )
            return response.choices[0].message.content.strip("\n")
        except Exception as e:
            return str(e).replace("\n", "    ")

    def evaluate(self, reference: dict, actual: dict) -> str:
        inputs = {}
        if "question_text" in reference:
            inputs["question_text"] = reference["question_text"]
        if "reference_answer" in reference:
            inputs["reference_answer"] = reference["reference_answer"]
        if "reference_steps" in reference:
            steps = reference["reference_steps"]
            inputs["reference_steps"] = "\n".join(s["output"] for s in steps)
        if "actual_answer" in actual:
            inputs["actual_answer"] = actual["actual_answer"]
        if "actual_steps" in actual:
            inputs["actual_context"] = actual["actual_steps"][-1]["output"]
            steps = actual["actual_steps"]
            inputs["actual_steps"] = "\n".join(s["output"] for s in steps)
        prompt = self.prompt_template.format(**inputs)
        return self.call_llm(prompt)
