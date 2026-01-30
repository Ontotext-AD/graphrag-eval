import json
import yaml
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator


RESERVED_KEYS = {
    "template_id",
    "question_id",
    "actual_answer",
    "actual_steps",
    "question_text",
    "reference_answer",
    "reference_steps",
    "status",
    "error",
    "answer_actual_claims_count",
    "answer_matching_claims_count",
    "answer_reference_claims_count",
    "answer_precision",
    "answer_recall",
    "answer_f1",
    "answer_correctness_reason",
    "answer_correctness_error"
    "answer_relevance",
    "answer_relevance_cost",
    "answer_relevance_reason",
    "answer_relevance_error",
    "steps_score",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "elapsed_sec",
}


Inputs = Literal[
    "question",
    "reference_answer",
    "reference_steps",
    "actual_answer",
    "actual_steps"
]

StepsKey = Literal["args", "output"]


class Config(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    inputs: list[Inputs] = Field(..., min_length=1)
    instructions: str
    outputs: dict[str, str]
    steps_name: str | None = None
    steps_keys: set[StepsKey] | None = Field(default=None, min_length=1)

    @model_validator(mode='after')
    def validate_step_dependencies(self) -> 'Config':
        if set(self.inputs) & {"reference_steps", "actual_steps"}:
            suffix = "is required when steps are in inputs"
            for var_name in ["steps_name", "steps_keys"]:
                if getattr(self, var_name) is None:
                    raise ValueError(f"{var_name} {suffix}")
        return self

    @model_validator(mode='after')
    def validate_name_and_outputs(self) -> 'Config':
        if self.name + "_error" in RESERVED_KEYS:
            raise ValueError(f"Name {self.name} is reserved")
        conflicting_keys = set(self.outputs.keys()) & RESERVED_KEYS
        if conflicting_keys:
            raise ValueError(f"Output keys {conflicting_keys} are reserved")
        return self

class Configs(RootModel):
    root: list[Config]


def create_input_template(input_key: str) -> str:
    header = input_key.replace("_", " ").capitalize()
    return f"# {header}\n{{{input_key}}}"


def create_prompt_template(config: Config, output_variables: list[str]) -> str:
    """
    Return a template for the LLM prompt, with placeholders for the inputs, 
    instructions, outputs etc. We use this template at evaluation time to
    format the actual values for the given question into a prompt.
    
    output_variables specifies the order of the outputs.
    """
    output_instructions = "Output the following values separated by tabs:"\
        + "".join(f"\n- {k}: {config.outputs[k]}" for k in output_variables)
    inputs_template = "\n\n".join(
        create_input_template(k) for k in config.inputs
    )
    return "\n\n".join([
        config.instructions.strip(),
        output_instructions,
        inputs_template,
    ])


class CustomEvaluator:
    def __init__(
        self, 
        config: Config,
        openai_model_name: str,
        temperature : float,
        openai_client,
    ):
        self.name = config.name
        self.input_variables = config.inputs
        self.steps_name = config.steps_name
        self.steps_keys = config.steps_keys
        self.output_variables = list(config.outputs.keys())
        self.prompt_template = create_prompt_template(
            config,
            self.output_variables
        )
        self.openai_client = openai_client
        self.openai_model_name = openai_model_name
        self.temperature = temperature

    def call_llm(self, prompt: str) -> str:
        try:
            response = self.openai_client.responses.create(
                model=self.openai_model_name,
                input=prompt,
                temperature=self.temperature
            )
            return response.output_text.strip("\n")
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
        result[self.name + '_error'] = msg
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
                    self.format_steps(group) 
                    for group in reference["reference_steps"]
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


def create_evaluators(
    config_file_path: str | Path | None, 
    openai_client, 
    openai_model_name, 
    temperature
) -> list[CustomEvaluator]:
        if config_file_path is None:
            return []
        with open(config_file_path, encoding="utf-8") as f:
            configs = yaml.safe_load(f)
        configs_list = Configs(configs)
        return [
            CustomEvaluator(c, openai_model_name, temperature, openai_client)
            for c in configs_list.root
        ]
