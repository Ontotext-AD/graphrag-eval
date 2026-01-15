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
        steps_keys: list[str],
        outputs: dict[str, str],
        instructions: str,
        temperature : float = TEMPERATURE
    ):
        self.metric_name = name
        self.input_variables = inputs
        self.steps_keys = steps_keys
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
        steps_out = []
        for step in steps:
            if isinstance(step, str):
                try:
                    step = json.loads(step)
                except json.JSONDecodeError:
                    pass
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
            steps_out.append(step_out)        
        return json.dumps(steps_out, indent=2)
    
    def parse_values(self, response: str) -> dict[str, str | None]:
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
        msg = f"Expected {n_exp} tab-separated values, got: {response}"
        result = dict(zip(self.output_variables, [None] * n_exp))
        result[self.metric_name + '_error'] = msg
        return result

    def evaluate(self, reference: dict, actual: dict) -> dict[str, str | None]:
        inputs = {}
        if "question" in self.input_variables:
            inputs["question"] = reference["question_text"]
        if "reference_answer" in self.input_variables:
            inputs["reference_answer"] = reference["reference_answer"]
        if "reference_context" in self.input_variables:
            context_str = json.loads(reference["reference_steps"][-1][-1]["output"])
            inputs["reference_context"] = json.dumps(context_str, indent=2)
        if "reference_steps" in self.input_variables:
            formatted_steps = [self.format_steps(ss) for ss in reference["reference_steps"]]
            inputs["reference_steps"] = "\n\n".join(formatted_steps)
        if "actual_answer" in self.input_variables:
            inputs["actual_answer"] = actual["actual_answer"]
        if "actual_context" in self.input_variables:
            context_str = json.loads(actual["actual_steps"][-1]["output"])
            inputs["actual_context"] = json.dumps(context_str, indent=2)
            with open("temp2.txt", "w") as f:
                f.write(inputs["actual_context"])
        if "actual_steps" in self.input_variables:
            inputs["actual_steps"] = self.format_steps(actual["actual_steps"])
        prompt = self.prompt_template.format(**inputs)
        with open("tests-with-openai/test_data/prompt.md", "w") as f:
            f.write(prompt)
        response = self.call_llm(prompt)
        return self.parse_values(response)


def parse_config(config_file_path: str | Path | None) -> list[CustomEvaluator]:
        if config_file_path is None:
            return []
        config = yaml.safe_load(open(config_file_path))
        return [CustomEvaluator(**c) for c in config]
