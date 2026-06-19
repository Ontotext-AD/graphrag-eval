# Output

[← README](../README.md)

The output is a list of objects, one for each reference item. Each output object includes fields copied from the reference item and corresponding target response record, plus computed metrics and other data. It can have the following keys.

- `template_id`: the template id
- `question_id`: the reference item id
- `question_text`: the natural language query or request text from the reference item
- `status`: `"success"` or `"error"`, indicating whether the target response record had an `error` field
- `error`: (optional) error message copied from the response record, if it had an `error` field
- `reference_steps`: (optional) copy of the expected steps from the reference item, if specified there. Additional key `matches` is added to matched reference steps.
- `reference_answer`: (optional) copy of the expected final response text, if supplied in the reference item
- `actual_answer`: (optional) copy of the final response text, if supplied in the target response record
- `answer_reference_claims_count`: (optional) number of claims extracted from `reference_answer`, if `reference_answer` and `actual_answer` are supplied
- `answer_actual_claims_count`: (optional) number of claims extracted from `actual_answer`, if `reference_answer` and `actual_answer` are supplied
- `answer_matching_claims_count`: (optional) number of matching claims between `reference_answer` and `actual_answer`, if both are supplied
- `answer_recall`: (optional) `answer_matching_claims_count / answer_reference_claims_count`
- `answer_precision`: (optional) `answer_matching_claims_count / answer_actual_claims_count`
- `answer_correctness_reason`: (optional) LLM reasoning in extracting and matching claims from `reference_answer` and `actual_answer`
- `answer_eval_error`: (optional) error message if answer evaluation failed
- `answer_f1`: (optional) Harmonic mean of `answer_recall` and `answer_precision`
- `answer_relevance`: (optional `float` in [0, 1]) answer relevance score
- `answer_relevance_error`: (optional) error message if answer relevance evaluation failed
- `actual_steps`: copy of the actual steps, or `[]` if missing from the target response record
- `steps_score`: (optional `float` in [0, 1]) steps score ([§ Steps score](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/steps.md#steps-score))
- `input_tokens`: (optional) input tokens usage
- `output_tokens`: (optional) output tokens usage
- `total_tokens`: (optional) total tokens usage
- `elapsed_sec`: (optional) elapsed seconds

Custom evaluations add top-level fields to each output object. These fields are defined by `custom_evaluations[*].outputs`; see [§ Custom metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/metrics.md#custom-metrics).

`actual_steps` with `name: "retrieval"` can contain the following keys:
- `retrieval_answer_recall`: (optional) recall of the retrieved context with respect to the reference answer, if evaluation succeeds
- `retrieval_answer_recall_error`: (optional) error message if `retrieval_answer_recall` evaluation fails
- `retrieval_answer_precision`: (optional) precision of the retrieved context with respect to the reference answer, if evaluation succeeds
- `retrieval_answer_precision_error`: (optional) error message if `retrieval_answer_precision` evaluation fails
- `retrieval_answer_f1`: (optional) F1 score of the retrieved context with respect to the reference answer, if `retrieval_answer_recall` and `retrieval_answer_precision` succeed
- `retrieval_context_recall`: (optional) recall of the retrieved context with respect to the reference context, if evaluation succeeds
- `retrieval_context_recall_error`: (optional) error message if `retrieval_context_recall` evaluation fails
- `retrieval_context_precision`: (optional) precision of the retrieved context with respect to the reference context, if evaluation succeeds
- `retrieval_context_precision_error`: (optional) error message if `retrieval_context_precision` evaluation fails
- `retrieval_context_f1`: (optional) F1 score of the retrieved context with respect to the reference context, if `retrieval_context_recall` and `retrieval_context_precision` succeed

## Aggregate metrics

Function `compute_aggregates()` takes in the computed evaluation metrics and aggregates them. The resulting aggregate metrics allow comparisons between agents with respect to quality, speed and token efficiency.

The aggregate metrics are organized as follows:
- `per_template`: a dictionary mapping a question template identifier to the following statistics:
    - `number_of_error_samples`: number of target response records for this template that had an `error` field
    - `number_of_success_samples`: number of target response records for this template that did not have an `error` field
    - `sum`, `mean`, `median`, `min` and `max` statistics of the following metrics (across the template's reference items where they exist):
        - `input_tokens`
        - `output_tokens`
        - `total_tokens`
        - `elapsed_sec`
        - `answer_recall`
        - `answer_precision`
        - `answer_f1`
        - `answer_relevance`
        - `steps_score`
        - `retrieval_answer_recall`
        - `retrieval_answer_precision`
        - `retrieval_answer_f1`
        - `retrieval_context_recall`
        - `retrieval_context_precision`
        - `retrieval_context_f1`
    - `steps`:
        - `total`: a map of step type to the number of times it was executed
        - `once_per_sample`: a map of step type to the number of reference items for which it was executed
        - `empty_results`: a map of step type to the number of times the step was executed and returned empty results
        - `errors`: a map of step type to the number of times the step was executed and resulted in error
- `micro`: statistics across reference items, regardless of template. It includes:
    - `number_of_error_samples`: number of target response records that had an `error` field
    - `number_of_success_samples`: number of target response records that did not have an `error` field
    - `steps`: includes:
        - `total`: a map of step type to the number of times it was executed
        - `once_per_sample`: a map of step type to the number of reference items for which it was executed
        - `empty_results`: a map of step type to the number of times the step was executed and returned empty results
        - `errors`: a map of step type to the number of times the step was executed and resulted in error
    - `sum`, `mean`, `median`, `min` and `max` statistics of the following metrics (across reference items where they exist):
        - `input_tokens`
        - `output_tokens`
        - `total_tokens`
        - `elapsed_sec`
        - `answer_recall`
        - `answer_precision`
        - `answer_f1`
        - `answer_relevance`
        - `retrieval_answer_recall`
        - `retrieval_answer_precision`
        - `retrieval_answer_f1`
        - `retrieval_context_recall`
        - `retrieval_context_precision`
        - `retrieval_context_f1`
        - `steps_score`
- `macro`: averages across templates, i.e., the mean of each metric per template, averaged. It includes the following means:
    - `input_tokens`
    - `output_tokens`
    - `total_tokens`
    - `elapsed_sec`
    - `answer_recall`
    - `answer_precision`
    - `answer_f1`
    - `answer_relevance`
    - `retrieval_answer_recall`
    - `retrieval_answer_precision`
    - `retrieval_answer_f1`
    - `retrieval_context_recall`
    - `retrieval_context_precision`
    - `retrieval_context_f1`
    - `steps_score`

See [example aggregate output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/examples/aggregates.yaml).
