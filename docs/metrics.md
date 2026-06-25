# Metrics

[← README](../README.md)

Below are the categories of supported metrics. Each metric has required fields from the reference item and target response record; it is computed if those fields are supplied. The output for each reference item includes keys for metrics and other data, listed in [§ Output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/output.md).


## Deterministic metrics

- Steps score: Correctness of the target response record's actual steps relative to the reference item's expected steps ([§ Steps score](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/steps.md#steps-score))
    - `steps_score`


## LLM-based metrics

All of the following metrics use an LLM. The LLM must be configured in a [configuration](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/config.md) file and its path passed as parameter `config_file_path=` to `run_evaluation()`. Specifically, all LLM-based metrics require a generation config.

- [RAGAS answer relevance](https://docs.ragas.io/en/v0.4.3/concepts/metrics/available_metrics/answer_relevance/). Also requires an embedding config.
    - `answer_relevance`

- Answer correctness: compare claims in `actual_answer` to claims in `reference_answer`. The claims are extracted from each final response text, counted and compared using an LLM. The counts are used to compute the metrics.
    - `answer_recall`
    - `answer_precision`
    - `answer_f1`

- Vector retrieval: compare retrieved context claims to reference claims, as with answer correctness:
    - **vs. reference answer**:
        - `retrieval_answer_recall`
        - `retrieval_answer_precision`
        - `retrieval_answer_f1`

    - **vs. reference context**:
        - `retrieval_context_recall`
        - `retrieval_context_precision`
        - `retrieval_context_f1`

- [custom metrics](#custom-metrics)

Supported LLM providers are all those supported by the [`litellm`](https://github.com/BerriAI/litellm) library, including all major LLMs and local LLMs via Ollama.


## Custom metrics

You can define your own metrics of target response records to be evaluated using an LLM. To do this, specify the metric name, inputs, outputs and instructions in a YAML file and pass the file path as a parameter to `run_evaluation()`. This will return your output metrics alongside the standard metrics described in previous sections.

One configuration file can define multiple custom evaluations, each of which will be done as a separate query to the LLM. Each evaluation can have multiple outputs. The format is shown in the example sections below.

See [§ Example configuration file with custom evaluation](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/config.md#example-configuration-file-with-custom-evaluations).

### Example call to evaluate using custom metrics

```python
from graphrag_eval import run_evaluation, compute_aggregates


evaluation_results = await run_evaluation(
    reference_qa_dataset, 
    chat_responses, 
    "my_project/eval_config_defining_custom_eval.yaml"
)
aggregates = compute_aggregates(
    evaluation_results,
    "my_project/eval_config_defining_custom_eval.yaml"
)
```

### Example output for custom metrics

With the [example custom metrics configuration](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/config.md#example-configuration-file-with-custom-evaluations), the output is as for [§ Example evaluation results](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/output.yaml), except that it has the following additional keys and example values:

```yaml
  my_answer_relevance: 0.9
  my_answer_relevance_reason: The answer contains relevant information except for the sentence about total revenue
  sparql_recall: 0.75
  sparql_precision: 0.6
  sparql_reason: The reference answer has 4 claims; there are 5 SPARQL results; 3 claims match
```

### Output in case of evaluation error

If there is an error during evaluation:
- The configured output keys will have value `null`
- There will be an additional key explaining the error. The key will be `{name}_error` where `name` is the custom evaluation name.

There are three types of error:
1. The reference item is missing keys requested in the custom evaluation configuration.
    - Example: `custom_1_error: Reference missing key 'reference_steps'`
2. The target response record is missing keys requested in the custom evaluation configuration.
    - Example: `custom_1_error: Actual output missing 'actual_steps'`
3. The evaluating LLM output does not conform to the custom evaluation configuration.
    - Example: `custom_1_error: "Expected 6 tab-separated values, got: 0.1\tCustom answer reason"`

### Recommendations

To improve custom evaluation accuracy:
1. Specify only a few outputs in each evaluation
1. Specify outputs explaining any quantities that the LLM must count or estimate. You can request one explanation per quantity or one shared explanation for several quantities.


## Aggregate metrics

These are the min, max, sum, mean, median of the above metrics ([§ Output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/output.md#aggregate-metrics)).

To compute them, call `compute_aggregates()`, passing the raw metrics as the first parameter.

To aggregate custom metrics, also pass the same path for `config_file_path=` as you passed to `run_evaluation()` to compute the raw custom metrics.
