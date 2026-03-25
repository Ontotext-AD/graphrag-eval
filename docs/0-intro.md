# Use as a Library

To evaluate answers and/or steps:
1. Install this package: section [Installation](installation.md)
1. Format the dataset of questions and reference answers and/or steps: section
   [Reference Q&A data](reference-qa-data.md)
1. Format the answers and/or steps you want to evaluate: section
   [Responses to evaluate](responses-to-evaluate.md)
1. To evaluate answer relevance:
    1. Include `actual_answer` in the target data to evaluate
    1. Set the appropriate environment variable (e.g.,`OPENAI_API_KEY`) with
       your LLM access key
1. To evaluate answer correctness:
    1. Include `reference_answer` in the reference dataset and `actual_answer`
       in the target data to evaluate
    1. Set the appropriate environment variable (e.g.,`OPENAI_API_KEY`) with
       your LLM access key
1. To evaluate steps:
    1. Include `reference_steps` in the reference data and `actual_steps` in
       target data to evaluate
1. If you want to evaluate metrics that require an LLM, write a
   [configuration file](configuration.md).
1. Call the evaluation function with the reference data and target data:
   section [Usage code](#usage-code)
1. Call the aggregation function with the evaluation results: sections
   [Usage code](#usage-code),
   [Aggregate output keys](output-keys.md#aggregates-keys) and
   [Example aggregates output](example-aggregates-output.md)

## Usage code

```python
from graphrag_eval import run_evaluation, compute_aggregates

reference_data: list[dict] = [] # Read your evaluation questions and reference answers
chat_responses: dict = {} # call your implementation to get responses to the questions
evaluation_results = await run_evaluation(reference_data, chat_responses)
aggregates = compute_aggregates(evaluation_results)
```

`evaluation_results` is a list of statistics for each question, as in section
[Evaluation results](evaluation-results.md). The format is explained in section
[Output Keys](output-keys.md)

If your chat responses contain actual answers, set your environment variable
`OPENAI_API_KEY` before running the code above.

# Command Line Use

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
