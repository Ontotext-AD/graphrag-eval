# Inputs

The input to the evaluator consists of two datasets of corresponding entries:
1. Reference dataset: questions and their reference answers
1. Actual dataset: the agent's answers and optionally executed steps

## Reference Q&A data

A reference dataset is a list of question "template" dicts, each of which contains:

- `template_id`: Unique template identifier, copied to the evaluation output
- `questions`: A list of questions derived from this template, where each includes:
  - `id`: Unique question identifier, matched to actual answer and copied to the evaluation output
  - `question_text`: The natural language query passed to the LLM
  - `reference_answer`: (optional) The expected answer to the question
  - `reference_steps`: (optional) A list of expected steps grouped by expected order of execution. All steps in a group can be executed in any order relative to each other, but after all steps in the previous group and before all steps in the next group. Each reference step dict can include:
    - `name`: The name of the step (e.g., `sparql_query`)
    - `args` (optional dict): Arguments to a tool used in the step. Examples:
      - SPARQL: keys such as `query`
      - Retrieval: tool-specific arguments
      - Time-series: keys such as `mrid`, `limit`
      - Data points: keys such as `external_id`, `granularity`, `aggregates`, `start`, `end`, `limit`
    - `output` (string): Expected output. For steps that compare structured results, provide a JSON-encoded string of the structure (e.g., SPARQL JSON results, retrieval contexts).
    - `output_media_type`: (optional, one of: missing, `application/sparql-results+json`, `application/json`) Controls how `output` is parsed and compared to actual output
    - `ordered`: (optional; default `false`) For SPARQL `SELECT` steps, whether row order matters. `true`: the actual result rows must be in the same order; `false`: result rows are matched as a set. Ignored for other step types.
    - `required_columns`: (optional list) For SPARQL `SELECT` steps, binding names required for query results that must match
    - `ignore_duplicates`: (optional list, defaults to `true`) For SPARQL `SELECT` results, whether duplicate rows are ignored when comparing actual vs. reference.

[Example reference dataset](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/reference.yaml) with two templates and associated questions and steps.

## Actual data

The actual data is a dict of `question_id` to a response dict. Each response dict contains:
- `question_id`: (required) Must equal `id` from the reference question; copied to the output
- `actual_answer` (optional) Enables `answer_relevance` and, if `reference_answer` exists and LLM is configured, answer correctness metrics
- `actual_steps` (optional list of dicts): Enables `steps_score` and retrieval step metrics if present ([§ Steps](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/steps.md)). Each actual step has:
  - `id`: uniqe step identifier. Used to annotate matched reference steps with `matches`.
  - `name`: Step type, used to match to a reference step for evaluation
  - `args` (optional dict): Arguments to a tool used in the step. Required for certain comparisons.
    - Retrieval steps (`name == "retrieval"`): must include `k` (the cutoff) so that ID-based recall@k can be computed against reference retrieval contexts.
    - Time series (`name == "retrieve_time_series"`): typically includes `mrid`, `limit`.
    - Data points (`name == "retrieve_data_points"`): typically includes `external_id`, `granularity`, `aggregates`, `start`, `end`, `limit`.
  - `output` (string): The actual output from the step
    - Retrieval: a JSON array of context objects. Each object should contain an `id` (required for ID-based recall@k). If you want text-based retrieval metrics (LLM-backed) to run, include the context text as well (e.g., `{"id": "...", "text": "..."}`).
    - SPARQL: a JSON object in SPARQL Results JSON format for `SELECT` or `ASK`.
  - `execution_timestamp` (`datetime`, timezone-aware preferred): Required for matching and evaluating `retrieve_data_points` steps. Used as an anchor for resolving relative times in the reference (e.g. `5m-ago`) to an absolute time for comaprison.
  - `status` (optional): Required value `"success"` for matching and evaluating the step.
  - `error` (optional): Marks an agent internal error for this question. 
  - `input_tokens`, `output_tokens`, `total_tokens`, `elapsed_sec` (numbers, optional): copied to the output and included in aggregates compyted by function `aggregate_metrics()` ([§ Output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/output.md)). Useful for analyzing your agent.

[Example actual answers dataset](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/actual.json).

## Keys by step type

- SPARQL (`sparql_query`):
  - Reference: `output_media_type == "application/sparql-results+json"`, `output` is SPARQL JSON results; `required_columns` (required for this comparison), `ordered` (optional), `ignore_duplicates` (optional).
  - Actual: `output` is SPARQL JSON results (as a JSON string).
- Retrieval (`retrieval`):
  - For steps_score (ID-based): compares reference vs actual context IDs using recall@k, where `k` is taken from the actual step’s `args.k`.
  - For LLM-backed retrieval metrics:
    - vs reference answer: runs when `reference_answer` exists and an LLM is configured; uses the actual step `output` (parsed JSON).
    - vs reference contexts: runs for matched retrieval steps when `reference_steps` include a retrieval step and an LLM is configured.
- Time series (`retrieve_time_series`):
  - Compares argument sets (`mrid`, `limit`), with normalization for multi-valued fields.
- Data points (`retrieve_data_points`):
  - Compares `external_id`, `granularity`, `aggregates`, `start`, `end`, `limit`; time bounds are compared using `execution_timestamp` as the anchor as described above.
- IRI discovery (`iri_discovery`):
  - Specialized comparator verifies discovery correctness (actual step tool may differ).

## Notes and tips

- For matching `steps_score`, see [Steps](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/steps.md).
- For per-question output schema and aggregate metrics, see [§ Output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/output.md)
