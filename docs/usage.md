# Use as a library

To evaluate answers and/or steps:
1. Install this package: section [Installation](installation.md)
1. Format the dataset of questions and reference answers and/or steps: section
   [Reference Q&A data](input.md#reference-qa-data)
1. Format the answers and/or steps to evaluate: section
   [Target responses to evaluate](input.md#target-responses-to-evaluate)
1. To evaluate metrics that require an LLM (section 
   [LLM use in evaluation](llm-use-in-evaluation.md)):
    1. Create a reference dataset and target dataset (output from the target
       system) with the relevant keys (section [Input](input.md)):
      1. For `answer_relevance` (section [Metrics](metrics.md)):
         1. include `actual_answer` in the reference dataset
      1. For answer correctness metrics (section [Metrics](metrics.md):
         1. include `reference_answer` in the reference dataset and 
            `actual_answer` in the target data to evaluate
      1. For custom metrics (section [Custom evaluation](custom-evaluation.md)):
         1. Define the metrics in the [configuration file](configuration.md)
         1. Include reference and target inputs used by the metrics
    1. Configure the LLM (section [configuration](configuration.md))
    1. Set the environment variable for your LLM provider (e.g.,
       `OPENAI_API_KEY`) to hold your LLM access key
1. To evaluate steps (section [Steps score](steps-score.md)):
    1. Include `reference_steps` in the reference data and `actual_steps` in
       target data
1. Call the evaluation function with the reference data and target data:
   section [Example code](#example-code)
1. Call the aggregation function with the evaluation results: sections
   [Example code](#example-code),
   [Aggregate output keys](output.md#aggregates-keys) and
   [Example aggregates output](examples/aggregates-output.yaml)

See also:
- [Example reference dataset](examples/reference-data.yaml)
- [Example target dataset](examples/target-data.json)

## Example code

```python
from graphrag_eval import run_evaluation, compute_aggregates

reference_data: list[dict] = [] # Read your evaluation questions and reference answers
chat_responses: dict = {} # call your implementation to get responses to the questions
evaluation_results = await run_evaluation(reference_data, chat_responses)
aggregates = compute_aggregates(evaluation_results)
```

`evaluation_results` is a list of statistics for each question, as in section
[Example evaluation results](examples/output.yaml). The format is explained in section
[Output Keys](output.md)

# Command-line use

To evaluate only correctness of final answers (system responses), you can
clone this repository and run the code on the command line:

1. Prepare an input TSV file with columns `Question`, `Reference answer` and
   `Actual answer`
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
