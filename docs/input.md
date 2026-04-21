# Inputs

The input to the library is two files of corresponding data items:
1. Reference data file: YAML list containing questions and their reference answers
1. Target data file: JSON list of the question responses by the agent we want to evaluate

## Reference Q&A data

A reference dataset is a list of templates, each of which contains:

- `template_id`: Unique template identifier
- `questions`: A list of questions derived from this template, where each includes:
  - `id`: Unique question identifier
  - `question_text`: The natural language query passed to the LLM
  - `reference_steps`: (optional) A list of expected steps grouped by expected order of execution. All steps in a group can be executed in any order relative to each other, but after all steps in the previous group and before all steps in the next group.
  - `reference_answer`: (optional) The expected answer to the question

This library is agnostic to the agent implementation and LLM model it uses; it depends only on the format of the response.

We assume that the final answer was derived from the outputs of the last executed steps.

Each step includes:

- `name`: The name of the step (e.g., `sparql_query`)
- `args`: Arguments of the step (e.g., arguments to a tool used in the step, such as a SPARQL query)
- `output`: The expected output from the step
- `output_media_type`: (optional; one of: missing, `application/sparql-results+json`, `application/json`) Indicates how the output of a step must be processed
- `ordered`: (for SPARQL; optional, defaults to `false`) For SPARQL query steps, whether results order matters. `true` means that the actual result rows must be ordered as the reference result; `false` means that result rows are matched as a set. Ignored for other step types.
- `required_columns`: (optional) Required only for SPARQL query results; list of binding names required for SPARQL query results to match
- `ignore_duplicates`: (optional, defaults to `true`) For SPARQL query results, whether duplicate binding values in the expected or in the actual results should be ignored for the comparison.

### Example

Here is an [example reference dataset](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/reference.yaml) with two templates and associated questions and steps.

## Target responses to evaluate

To evaluate responses by the target agent against the reference responses, format the target responses as in this [example target dataset](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/target.json).

The aggregate metrics output by function `aggregate_metrics()` include the number of questions for which the agent experienced an internal error. To mark a response to be tallied as an error, set the following keys in it:
* `status` key to value `"error"`
* `error` to describe the error

Example:

```json
{
    "question_id": "a8daaf98b84b4f6b0e0052fb942bf6b6",
    "status": "error",
    "error": "Error message"
}
```
