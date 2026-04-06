# Output

The output is a list of objects corresponding to questions from the reference Q&A dataset. Each output object includes computed metrics and other data. It can have the following keys.

- `template_id`: the template id
- `question_id`: the question id
- `question_text`: the natural language query
- `status`: "success" or "error", indicating whether the evaluation succeeded
- `reference_steps`: (optional) copy of the expected steps in the Q&A dataset, if specified there. Additional key "matches" is added to those steps which are matched.
- `reference_answer`: (optional) copy of the expected answer text, if supplied in the reference data
- `actual_answer`: (optional) copy of the response text, if supplied in the target data
- `answer_reference_claims_count`: (optional) number of claims extracted from the reference answer, if a reference answer and actual answer are supplied
- `answer_actual_claims_count`: (optional) number of claims extracted from the actual answer, if a reference answer and actual answer are supplied
- `answer_matching_claims_count`: (optional) number of matching claims between the reference answer and the actual answer, if a reference answer and actual answer are supplied
- `answer_recall`: (optional) `answer_matching_claims_count / answer_reference_claims_count`
- `answer_precision`: (optional) `answer_matching_claims_count / answer_actual_claims_count`
- `answer_correctness_reason`: (optional) LLM reasoning in extracting and matching claims from the reference answer text and the actual answer text
- `answer_eval_error`: (optional) error message if answer evaluation failed
- `answer_f1`: (optional) Harmonic mean of `answer_recall` and `answer_precision`
- `answer_relevance`: (optional `float` in [0, 1]) answer relevance score
- `answer_relevance_error`: (optional) error message if answer relevance evaluation failed
- `actual_steps`: (optional) copy of the actual steps, if specified the target data
- `steps_score`: (optional `float` in [0, 1]) steps score (section [Steps score](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/steps.md#steps-score))
- `input_tokens`: (optional) input tokens usage
- `output_tokens`: (optional) output tokens usage
- `total_tokens`: (optional) total tokens usage
- `elapsed_sec`: (optional) elapsed seconds

All `actual_steps` with `name` "retrieval" contain the following keys:
- `retrieval_answer_recall`: (optional) recall of the retrieved context with respect to the reference answer, if evaluation succeeds
- `retrieval_answer_recall_error`: (optional) error message if `retrieval_answer_recall` evaluation fails
- `retrieval_answer_precision`: (optional) precision of the retrieved context with respect to the reference answer, if evaluation succeeds
- `retrieval_answer_precision_error`: (optional) error message if `retrieval_answer_precision` evaluation fails
- `retrieval_answer_f1`: (optional) F1 score of the retrieved context with respect to the reference answer, if `retrieval_answer_recall` and `retrieval_answer_precision` succeed
- `retrieval_context_recall`: (optional) recall of the retrieved context with respect to the reference context, if evaluation succeeds
- `retrieval_context_recall_error`: (optional) error message if `retrieval_context_recall` evaluation fails
- `retrieval_context_precision`: (optional) precision of the retrieved context with respect to the reference context, if evaluation succeeds
- `retrieval_context_precision_error`: (optional) error message if `retrieval_context_precision` evaluation fails
- `retrieval_context_f1`: (optional) F1 score of the retrieved context with respect to the reference answer, if `retrieval_context_recall` and `retrieval_context_precision` succeed

## Aggregate metrics

Function `compute_aggregates()` takes in the computed evaluation metrics and aggregates them. The resulting aggregate metrics allow comparisons between agents with respect to quality, speed and token efficiency.

The aggregate metrics are organized as follows:
- `per_template`: a dictionary mapping a question template identifier to the following statistics:
  - `number_of_error_samples`: number of questions of this template which resulted in an error response
  - `number_of_success_samples`: number of questions of this template which resulted in a successful response
  - `sum`, `mean`, `median`, `min` and `max` statistics of the following metrics (across the template's questions where they exist):
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
      - `once_per_sample`: a map of step type to the number of questions for which it was executed
      - `empty_results`: a map of step type to the number of times the step was executed and returned empty results
      - `errors`: a map of step type to the number times the step was executed and resulted in error
- `micro`: statistics across questions, regardless of template. It includes:
  - `number_of_error_samples`: number of questions which resulted in error response
  - `number_of_success_samples`: number of questions which resulted in successful response
  - `steps`: includes:
      - `total`: a map of step type to the number of times it was executed
      - `once_per_sample`: a map of step type to the number of questions for which it was executed
      - `empty_results`: a map of step type to the number of times the step was executed and returned empty results
      - `errors`: a map of step type to the number times the step was executed and resulted in error
  - `sum`, `mean`, `median`, `min` and `max` statistics of the following metrics (across questions where they exist):
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
