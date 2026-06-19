# Quickstart

[← README](../README.md)

## Installation

Choose a tier below.

### Basic (no LLM)

Evaluates steps of types:
- SPARQL query
- time series
- data points

Install using pip:

```bash
pip install graphrag-eval
```

or add the following dependency in your `pyproject.toml` file:

```toml
graphrag-eval = "*"
```

### Full

Includes metrics that use an LLM ([§ LLM-based metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/metrics.md#llm-based-metrics)):
- answer relevance
- answer correctness
- retrieval steps
- [custom metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/metrics.md#custom-metrics)

Install with the `llm` extra. Using pip:

```bash
pip install 'graphrag-eval[llm]'
```

or add the following dependency in your `pyproject.toml` file:

```toml
graphrag-eval = {version = "*", extras = ["llm"]}
```


## Usage

### Use as a library

To evaluate answers and/or steps:
1. Install this package ([§ Installation](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/quickstart.md#installation))
1. Format the reference items ([§ Reference items](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/input.md#reference-items))
1. Format the target response records to evaluate ([§ Target response records](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/input.md#target-response-records))
1. To evaluate metrics that require an LLM ([§ LLM use in evaluation](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/metrics.md#llm-based-metrics)):
    1. Include the relevant keys for all reference items and target response records ([§ Inputs](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/input.md)):
        1. For `answer_relevance` ([§ Metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/metrics.md)):
            1. Include `actual_answer` in the target response record
        1. For answer correctness metrics ([§ Metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/metrics.md)):
            1. Include `reference_answer` in the reference item and `actual_answer` in the target response record
        1. For custom metrics ([§ Custom metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/metrics.md#custom-metrics)):
            1. Define the metrics ([§ Configuration](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/config.md))
            1. Include the reference item and target response record fields specified in the definitions
    1. Configure the LLM ([§ Configuration](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/config.md))
    1. Set the environment variable for your LLM provider (e.g., `OPENAI_API_KEY`) to hold your LLM API key
1. To evaluate steps ([§ Steps score](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/steps.md)):
    1. Include `reference_steps` in reference items and `actual_steps` in target response records
1. Call `run_evaluation()`, passing the reference dataset, target response records, and optionally a configuration file path ([§ Example code](#example-code))
1. Call `compute_aggregates()`, passing the evaluation results and the config file path if you passed one to `run_evaluation()` ([§ Example code](#example-code), [§ Aggregate metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/output.md#aggregate-metrics), [§ Example aggregate output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/aggregates.yaml))

See also:
- [Example reference dataset](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/reference.yaml)
- [Example target dataset](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/target.json)

#### Example code

```python
import asyncio
import yaml

from graphrag_eval import run_evaluation, compute_aggregates


async def main():
    with open("reference_data.yaml", encoding="utf-8") as f:
        reference_data: list[dict] = yaml.safe_load(f)

    response_records = {}
    for template in reference_data:
        for reference_item in template["questions"]:
            question_id = reference_item["id"]
            actual_answer = await agent(reference_item["question_text"])
            response_records[question_id] = {
                "question_id": question_id,
                "actual_answer": actual_answer,
            }

    config_file_path = "my_project/eval_config.yaml"  # Optional

    evaluation_results = await run_evaluation(
        reference_data,
        response_records,
        config_file_path=config_file_path,
    )
    aggregates = compute_aggregates(
        evaluation_results,
        config_file_path=config_file_path,
    )


asyncio.run(main())
```

`config_file_path` is optional ([§ Configuration](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/config.md)). Provide it to configure an LLM ([§ LLM use in evaluation](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/metrics.md#llm-based-metrics)) or custom metrics ([§ Custom metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/metrics.md#custom-metrics)).

The result `evaluation_results` is a list of objects, one for each reference item ([§ Output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/output.md)) as shown in this [Example output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/output.yaml).

### Command-line use

To evaluate only correctness of final answers (system responses), you can clone this repository and run the code on the command line:

1. Prepare an input TSV file with columns `Question`, `Reference answer` and `Actual answer`
1. Clone this repository (`git clone https://github.com/Ontotext-AD/graphrag-eval.git`)
1. Install [Python Poetry](https://python-poetry.org/)
1. Execute `poetry install --with llm`
1. Execute
   ```
   <LLM_ACCESS_VARIABLE>=<your_api_key> poetry run answer-correctness -i <input_file.tsv> -o <output_file.tsv> -c <config.yaml>
   ```
   replacing `<LLM_ACCESS_VARIABLE>` with the variable used by your LLM provider
   to specify your LLM API key.
   Example:
   ```
   OPENAI_API_KEY=XXX poetry run answer-correctness -i reference.tsv -o evaluations.tsv -c conf.yaml
   ```
