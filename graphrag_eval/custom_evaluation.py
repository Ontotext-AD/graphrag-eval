import json
import yaml
from pathlib import Path

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
        outputs: dict[str, str],
        instructions: str,
        steps_name: str,
        steps_keys: list[str] | None = None,
        temperature : float = TEMPERATURE
    ):
        self.metric_name = name
        self.input_variables = inputs
        self.steps_name = steps_name
        self.steps_keys = steps_keys or ["args", "output"]
        outputs_tuples = list(outputs.items())
        self.output_variables = list(zip(*outputs_tuples))[0]
        inputs_template = "\n\n".join(format_input_template(i) for i in inputs)
        output_instructions = "Output the following values separated by tabs:"\
            + "".join(f"\n* {n}: {d}" for n, d in outputs_tuples)
        self.prompt_template = "\n\n".join([
            instructions.strip(),
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

    def format_steps(self, steps: list) -> str:
        steps_formatted = []
        for step in steps:
            if isinstance(step, str):
                step = json.loads(step)
            if step["name"] != self.steps_name:
                continue
            step_out = {}
            for k in self.steps_keys:
                val = step.get(k)
                if isinstance(val, str):
                    try:
                        step_out[k] = json.loads(val)
                    except (json.JSONDecodeError, TypeError):
                        step_out[k] = val
                else:
                    step_out[k] = val
            steps_formatted.append(step_out)        
        return json.dumps(steps_formatted, indent=2)
    
    def error(self, msg: str) -> dict:
        result = {k: None for k in self.output_variables}
        result[self.metric_name + '_error'] = msg
        return result

    def parse_outputs(self, response: str) -> dict[str, str | None]:
        vals = response.split("\t")
        n_act = len(vals)
        n_exp = len(self.output_variables)
        if n_act == n_exp:
            result = {}
            for k, v in zip(self.output_variables, vals):
                try:
                    v = json.loads(v)
                except json.decoder.JSONDecodeError:
                    pass
                result[k] = v
            return result
        return self.error(f"Expected {n_exp} tab-separated values, got: {response}")

    def evaluate(self, reference: dict, actual: dict) -> dict[str, str | None]:
        inputs = {}
        if "question" in self.input_variables:
            if "question_text" not in reference:
                return self.error("Missing 'question_text' in reference")
            inputs["question"] = reference["question_text"]
        if "reference_answer" in self.input_variables:
            if "reference_answer" not in reference:
                return self.error("Missing 'reference_answer' in reference")
            inputs["reference_answer"] = reference["reference_answer"]
        if "actual_answer" in self.input_variables:
            if "actual_answer" not in actual:
                return self.error("Actual output missing 'actual_answer'")
            inputs["actual_answer"] = actual["actual_answer"]
        if "reference_steps" in self.input_variables \
        or "actual_steps" in self.input_variables:
            if not self.steps_name:
                msg = "Field 'steps_name' is required for input 'steps'"
                return self.error(msg)
        if "reference_steps" in self.input_variables:
            if "reference_steps" not in reference:
                return self.error("Reference missing key 'reference_steps'")
            try:
                formatted_steps_lists = [
                    self.format_steps(ss) 
                    for ss in reference["reference_steps"]
                ]
            except json.JSONDecodeError:
                return self.error("Malformed reference step JSON")
            inputs["reference_steps"] = "\n\n".join(formatted_steps_lists)
        if "actual_steps" in self.input_variables:
            if "actual_steps" not in actual:
                return self.error("Actual output missing 'actual_steps'")
            try:
                formatted_steps_lists = self.format_steps(actual["actual_steps"])
            except json.JSONDecodeError:
                return self.error("Malformed actual step JSON")
            inputs["actual_steps"] = formatted_steps_lists
        prompt = self.prompt_template.format(**inputs)
        response = self.call_llm(prompt)
        return self.parse_outputs(response)


def parse_config(config_file_path: str | Path | None) -> list[CustomEvaluator]:
        if config_file_path is None:
            return []
        with open(config_file_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return [CustomEvaluator(**c) for c in config]
