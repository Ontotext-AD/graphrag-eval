# Inputs

The input to the library consists of two files of data sets with corresponding entries:
1. Reference dataset: a list of questions and their reference answers
1. Target dataset: the question responses by the system we want to evaluate

## Reference Q&A data

A reference dataset is a list of templates, each of which contains:

- `template_id`: Unique template identifier
- `questions`: A list of questions derived from this template, where each includes:
  - `id`: Unique question identifier
  - `question_text`: The natural language query passed to the LLM
  - `reference_steps`: (optional) A list of expected steps grouped by expected order of execution. All steps in a group can be executed in any order relative to each other, but after all steps in the previous group and before all steps in the next group.
  - `reference_answer`: (optional) The expected answer to the question

This library is agnostic to the question-answering system implementation and LLM model it uses; it depends only on the format of the response.

The assumption is that the final answer to the question is derived from the outputs of the steps, which are executed last (last level).

Each step includes:

- `name`: The name of the step (e.g., `sparql_query`)
- `args`: Arguments of the step (e.g., arguments to a tool used in the step, such as a SPARQL query)
- `output`: The expected output from the step.
- `output_media_type`: (optional, missing or one of `application/sparql-results+json`, `application/json`) Indicates how the output of a step must be processed
- `ordered`: (optional, defaults to `false`) For SPARQL query results, whether results order matters. `true` means that the actual result rows must be ordered as the reference result; `false` means that result rows are matched as a set.
- `required_columns`: (optional) - required only for SPARQL query results; list of binding names, which are required for SPARQL query results to match
- `ignore_duplicates`: (optional, defaults to `true`) For SPARQL query results, whether duplicate binding values in the expected or in the actual results should be ignored for the comparison.

### Example

Here is an [example Q&A dataset reference dataset](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/reference.yaml) with two templates and associated questions and steps.

## Target responses to evaluate

To evaluate responses by the target agent against the reference responses, format the target responses as in this [example target dataset](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/target.json).

On the other hand, to tally a response as an error in generating the response, format the target response as in this example:

```json
{
    "question_id": "a8daaf98b84b4f6b0e0052fb942bf6b6",
    "error": "Error message",
    "status": "error"
}
```
