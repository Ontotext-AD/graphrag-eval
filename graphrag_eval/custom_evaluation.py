import yaml

from openai import OpenAI


LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.0


class CustomEvaluator:
    def __init__(
        self, config_file_path: str,
        temperature : float = TEMPERATURE
    ):
        config = yaml.safe_load(open(config_file_path))
        self.metric_name = config["name"]
        self.input_variables = config["inputs"]
        self.n_outputs = config["n_outputs"]
        self.prompt_template = config["instructions"]
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

    def format_steps(self, steps: list[dict]) -> str:
        keys = self.input_variables["reference_steps"]
        step_strs = []
        for step in steps:
            step_out = {k: step[k] for k in keys}
            step_strs.append(str(step_out))
        return "\n\n".join(step_strs)

    def parse_values(self, response: str) -> list[str | None]:
        vals = response.split("\t")
        act_n = len(vals)
        if act_n == self.n_outputs:
            return vals
        msg = f"Expected {self.n_outputs} tab-separated values: {response}"
        return [] * self.n_outputs + [msg]
    
    def evaluate(self, reference: dict, actual: dict) -> list[str | None]:
        inputs = {}
        if "question" in self.input_variables:
            inputs["question_text"] = reference["question_text"]
        if "reference_answer" in self.input_variables:
            inputs["reference_answer"] = reference["reference_answer"]
        if "reference_steps" in self.input_variables:
            inputs["reference_steps"] = self.format_steps(reference["reference_steps"])
        if "actual_answer" in self.input_variables:
            inputs["actual_answer"] = actual["actual_answer"]
        if "actual_context" in self.input_variables:
            inputs["actual_context"] = actual["actual_steps"][-1]["output"]
        if "actual_steps" in self.input_variables:
            inputs["actual_steps"] = self.format_steps(actual["actual_steps"])
        prompt = self.prompt_template.format(**inputs)
        response = self.call_llm(prompt)
        return self.parse_values(response)
