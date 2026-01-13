import yaml

from openai import OpenAI


LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.0

def format_input_template(input_config: str | dict[str, list[str]]) -> str:
    if isinstance(input_config, str):
        k = input_config
    elif isinstance(input_config, dict):
        k = list(input_config.keys())[0]
    else:
        raise ValueError(f"Invalid input format: {input_config}")
    header = k.replace("_", " ").capitalize()
    return f"# {header}\n{{{k}}}"


class CustomEvaluator:
    def __init__(
        self, 
        name: str,
        inputs: list[str],
        outputs: list[str],
        instructions: str,
        temperature : float = TEMPERATURE
    ):
        self.metric_name = name
        self.input_variables = inputs
        self.output_variables = outputs
        inputs_template = "\n\n".join(format_input_template(i) for i in inputs)
        output_instructions = "Output the following values separated by tabs:"\
            + "".join(f"\n* {o}" for o in outputs)
        self.prompt_template = "\n\n".join([
            instructions,
            output_instructions,
            inputs_template,
        ])
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
        exp_n = len(self.output_variables)
        if act_n == exp_n:
            return vals
        msg = f"Expected {exp_n} tab-separated values: {response}"
        return [] * exp_n + [msg]
    
    def evaluate(self, reference: dict, actual: dict) -> list[str | None]:
        inputs = {}
        if "question" in self.input_variables:
            inputs["question_text"] = reference["question_text"]
        if "reference_answer" in self.input_variables:
            inputs["reference_answer"] = reference["reference_answer"]
        if "reference_context" in self.input_variables:
            inputs["reference_context"] = reference["reference_steps"][-1]["output"]
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


def parse_config(config_file_path: str | None) -> list[CustomEvaluator]:
        if config_file_path is None:
            return []
        config = yaml.safe_load(open(config_file_path))
        return [CustomEvaluator(**c) for c in config]
