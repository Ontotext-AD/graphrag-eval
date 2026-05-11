# Usage

## Use as a library

To evaluate answers and/or steps:
1. Install this package ([§ Installation](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/install.md))
1. Format the dataset of questions and reference answers and/or steps ([§ Reference Q&A data](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/input.md#reference-qa-data))
1. Format the answers and/or steps to evaluate ([§ Target responses to evaluate](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/input.md#target-responses-to-evaluate))
1. To evaluate metrics that require an LLM ([§ LLM use in evaluation](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/llm.md)):
    1. Include the relevant keys for all questions ([§ Inputs](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/input.md)):
        1. For `answer_relevance` ([§ Metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/metrics.md)):
            1. Include `actual_answer` in target data
        1. For answer correctness metrics ([§ Metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/metrics.md)):
            1. Include `reference_answer` in reference data and `actual_answer` in target data to evaluate
        1. For custom metrics ([§ Custom evaluation](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/custom.md)):
            1. Define the metrics ([§ Configuration](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/config.md))
            1. Include reference and target inputs specified in the definitions
     1. Configure the LLM ([§ Configuration](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/config.md))
     1. Set the environment variable for your LLM provider (e.g., `OPENAI_API_KEY`) to hold your LLM API key
1. To evaluate steps ([§ Steps score](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/steps.md)):
  1. Include `reference_steps` in reference data and `actual_steps` in target data
1. Call function `run_evaluation()`, passing to it the reference data, target data: [§ Example code](#example-code) and optionally a configuration file path
1. Call function `compute_aggregates()`, passing the evaluation results and the path to the config file if you passed one to `run_evaluation()` ([§ Example code](#example-code), [§ Aggregate metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/output.md#aggregate-metrics), [§ Example aggregate output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/aggregates.yaml))

See also:
- [Example reference dataset](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/reference.yaml)
- [Example target dataset](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/target.json)

### Example code

```python
import yaml
from graphrag_eval import run_evaluation, compute_aggregates

# Read your evaluation questions and reference answers
with open("my_reference_dataset.yaml") as f:
    reference_data: list[dict] = yaml.safe_load(f)

# Extract a list of questions
question_texts = [
    question["question_text"]
    for template in reference_data 
    for question in template["questions"]
]

# Call your implementation to get its responses to the questions
chat_responses: dict = my_agent(question_texts)

# Evaluate
evaluation_results = await run_evaluation(
    reference_qa_dataset, 
    chat_responses, 
    config_file_path="my_project/eval_config.yaml"  # Optional
)
aggregates = compute_aggregates(
    evaluation_results,
    config_file_path="my_project/eval_config.yaml"  # Must be as run_evaluation(config_file_path=)
)
```

Parameter `config_file_path` is optional ([§ Configuration](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/configure.md)). It allows you to configure an LLM ([§ LLM use in evaluation)](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/llm.md)) and cutom metrics ([§ Custom evaluation (custom metrics)](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/custom.md)).

The result `evaluation_results` is a list of objects, one for each question ([§ Output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/output.md)) as shown in this [Example output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/output.yaml).

## Command-line use

To evaluate only correctness of final answers (system responses), you can clone this repository and run the code on the command line:

1. Prepare an input TSV file with columns `Question`, `Reference answer` and `Actual answer`
1. Clone this repository (`git clone https://github.com/Ontotext-AD/graphrag-eval.git`)
1. Install [Python Poetry](https://python-poetry.org/)
1. Execute `poetry install --with llm`
1. Execute
   ```
   <LLM_ACCESS_VARIABLE>=<your_api_key> poetry run answer-correctness -i <input_file.tsv> -o <output_file.tsv>
   ```
   replacing `<LLM_ACCESS_VARIABLE>` by the variable used by your LLM provider
   to specify your LLM use key.
   Example:
   ```
   OPENAI_API_KEY=XXX poetry run answer-correctness -i reference.tsv -o evaluations.tsv
   ```
