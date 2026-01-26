import json
import yaml
from pathlib import Path

from openai import OpenAI


LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.0


def create_input_template(input_key: str) -> str:
    header = input_key.replace("_", " ").capitalize()
    return f"# {header}\n{{{input_key}}}"


class CustomEvaluator:
    def __init__(
        self, 
        name: str,
        inputs: list[str],
        outputs: dict[str, str],
        instructions: str,
        steps_name: str | None = None,
        steps_keys: list[str] | None = None,
        temperature : float = TEMPERATURE
    ):
        self.metric_name = name
        self.input_variables = inputs
        self.steps_name = steps_name
        self.steps_keys = steps_keys
        outputs_tuples = list(outputs.items())
        self.output_variables = list(zip(*outputs_tuples))[0]
        inputs_template = "\n\n".join(create_input_template(k) for k in inputs)
        output_instructions = "Output the following values separated by tabs:"\
            + "".join(f"\n- {k}: {desc}" for k, desc in outputs_tuples)
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
                return self.error("Reference missing key 'question_text'")
            inputs["question"] = reference["question_text"]
        if "reference_answer" in self.input_variables:
            if "reference_answer" not in reference:
                return self.error("Reference missing key 'reference_answer'")
            inputs["reference_answer"] = reference["reference_answer"]
        if "actual_answer" in self.input_variables:
            if "actual_answer" not in actual:
                return self.error("Actual output missing key 'actual_answer'")
            inputs["actual_answer"] = actual["actual_answer"]
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
                return self.error("Actual output missing key 'actual_steps'")
            try:
                formatted_steps_lists = self.format_steps(actual["actual_steps"])
            except json.JSONDecodeError:
                return self.error("Malformed actual step JSON")
            inputs["actual_steps"] = formatted_steps_lists
        prompt = self.prompt_template.format(**inputs)
        response = self.call_llm(prompt)
        return self.parse_outputs(response)


MANDATORY_KEYS = ["name", "inputs", "instructions", "outputs"]


class ConfigError(Exception):
    pass


def _check_config(err_prefix: str, config: dict) -> None:
    if not isinstance(config, dict):
        raise ConfigError(f"{err_prefix} should be a dict, got {type(config)}")
    for key in MANDATORY_KEYS:
        if key not in config:
            raise ConfigError(f"{err_prefix} should have key '{key}'")
    for key in ["reference_steps", "actual_steps"]:
        if key in config:
            if not isinstance(config[key], list):
                raise ConfigError(f"{err_prefix} key '{key}' should be a list")
    if set(["reference_steps", "actual_steps"]) & set(config["inputs"]):
        for key in "steps_name", "steps_keys":
            if key not in config:
                raise ConfigError(f"{err_prefix} should have key '{key}'")
        if set(config["steps_keys"]) - {"args", "output"}:
            raise ConfigError(
                f"{err_prefix} key 'steps_keys' values can only include "
                "'args', 'output'"
            )
    

def parse_config(config_file_path: str | Path | None) -> list[CustomEvaluator]:
        if config_file_path is None:
            return []
        try:
            with open(config_file_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            raise ConfigError(f"Config file not found at {config_file_path}")
        msg = "Custom configuration"
        if not isinstance(config, list):
            raise ConfigError(f"{msg} should be a list, got {type(config)}")
        evaluators = []
        for i, c in enumerate(config):
            _check_config(f"{msg} {i}", c)
            evaluators.append(CustomEvaluator(**c))
        return evaluators
