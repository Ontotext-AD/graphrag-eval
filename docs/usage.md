# Usage

## Use as a library

To evaluate answers and/or steps:
1. Install this package ([§ Installation](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/install.md))
1. Format the dataset of questions and reference answers and/or steps ([§ Reference Q&A data](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/input.md#reference-qa-data))
1. Format the answers and/or steps to evaluate: [§ Target responses to evaluate](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/input.md#target-responses-to-evaluate)
1. To evaluate metrics that require an LLM ([§ LLM use in evaluation](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/llm.md)):
  1. Create a reference dataset and target dataset (output from the target system) with the relevant keys ([§ Inputs](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/input.md)):
    1. For `answer_relevance` ([§ Metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/metrics.md)):
      1. Include `actual_answer` in the reference dataset
    1. For answer correctness metrics ([§ Metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/metrics.md)):
      1. Include `reference_answer` in the reference dataset and `actual_answer` in the target data to evaluate
    1. For custom metrics ([§ Custom evaluation](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/custom.md)):
      1. Define the metrics ([§ Configuration](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/config.md))
      1. Include reference and target inputs used by the metrics
  1. Configure the LLM ([§ Configuration](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/config.md))
  1. Set the environment variable for your LLM provider (e.g., `OPENAI_API_KEY`) to hold your LLM access key
1. To evaluate steps ([§ Steps score](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/steps.md)):
  1. Include `reference_steps` in the reference data and `actual_steps` in target data
1. Call the evaluation function with the reference data and target data: [§ Example code](#example-code)
1. Call the aggregation function with the evaluation results: sections [Example code](#example-code), [Aggregate metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/output.md#aggregate-metrics) and [Example aggregate output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/aggregates.yaml)

See also:
- [Example reference dataset](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/reference.yaml)
- [Example target dataset](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/target.json)

### Example code

```python
from graphrag_eval import run_evaluation, compute_aggregates

reference_data: list[dict] = [] # Read your evaluation questions and reference answers
chat_responses: dict = {} # call your implementation to get responses to the questions
evaluation_results = await run_evaluation(reference_data, chat_responses)
aggregates = compute_aggregates(evaluation_results)
```

`evaluation_results` is a list of objects, one for each question ([§ Output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/output.md)) as shown in this [Example output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/output.yaml).

## Command-line use

To evaluate only correctness of final answers (system responses), you can clone this repository and run the code on the command line:

1. Prepare an input TSV file with columns `Question`, `Reference answer` and `Actual answer`
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
