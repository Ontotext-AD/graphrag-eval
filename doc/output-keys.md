### Output Keys

- `template_id`: the template id
- `question_id`: the question id
- `question_text`: the natural language query
- `status`: "success" or "error", indicating whether the evaluation succeeded
- `reference_steps`: (optional) copy of the expected steps in the Q&A dataset, 
if specified there. Additional key "matches" is added to those steps, which are 
matched.
- `reference_answer`: (optional) copy of the expected answer in the Q&A dataset, if specified there
- `actual_answer`: (optional) copy of the response text in the evaluation target, if specified there
- `answer_reference_claims_count`: (optional) number of claims extracted from the reference answer, if a reference answer and actual answer are available
- `answer_actual_claims_count`: (optional) number of claims extracted from the answer being evaluated, if a reference answer and actual answer are available
- `answer_matching_claims_count`: (optional) number of matching claims between the reference answer and the actual answer, if a reference answer and actual answer are available
- `answer_recall`: (optional) `answer_matching_claims_count / answer_reference_claims_count`
- `answer_precision`: (optional) `answer_matching_claims_count / answer_actual_claims_count`
- `answer_correctness_reason`: (optional) LLM reasoning in extracting and matching claims from the reference answer and the actual answer
- `answer_eval_error`: (optional) error message if answer evaluation failed
- `answer_f1`: (optional) Harmonic mean of `answer_recall` and `answer_precision`
- `answer_relevance`: (optional) The value representing how relevant is the actual answer to the question, computed using [RAGAS answer relevance](https://docs.ragas.io/en/v0.3.3/concepts/metrics/available_metrics/answer_relevance/)
- `answer_relevance_error`: (optional) error message if answer relevance evaluation failed
- `answer_relevance_cost`: (optional) The LLM use cost of computing 
`answer_relevance`, in US dollars
- `actual_steps`: (optional) copy of the steps in the evaluation target, if specified there
- `steps_score`: (optional) a real number between 0 and 1, see how step score 
is calculated in the section [Steps score](#Steps-score)
- `input_tokens`: (optional) input tokens usage
- `output_tokens`: (optional) output tokens usage
- `total_tokens`: (optional) total tokens usage
- `elapsed_sec`: (optional) elapsed seconds

All `actual_steps` with `name` "retrieval" contain:
- `retrieval_answer_recall`: (optional) recall of the retrieved context with respect to the reference answer, if evaluation succeeds
- `retrieval_answer_recall_reason`: (optional) LLM reasoning in evaluating `retrieval_answer_recall`
- `retrieval_answer_recall_error`: (optional) error message if `retrieval_answer_recall` evaluation fails
- `retrieval_answer_recall_cost`: cost of evaluating `retrieval_answer_recall`, in US dollars
- `retrieval_answer_precision`: (optional) precision of the retrieved context with respect to the reference answer, if evaluation succeeds
- `retrieval_answer_precision_error`: (optional) error message if `retrieval_answer_precision` evaluation fails
- `retrieval_answer_precision_cost`: cost of evaluating `retrieval_answer_precision`, in US dollars
- `retrieval_answer_f1`: (optional) F1 score of the retrieved context with respect to the reference answer, if `retrieval_answer_recall` and `retrieval_answer_precision` succeed
- `retrieval_answer_f1_cost`: The sum of `retrieval_answer_recall_cost` and `retrieval_answer_precision_cost`
- `retrieval_context_recall`: (optional) recall of the retrieved context with respect to the reference answer, if evaluation succeeds
- `retrieval_context_recall_error`: (optional) error message if `retrieval_context_recall` evaluation fails
- `retrieval_context_precision`: (optional) precision of the retrieved context with respect to the reference answer, if evaluation succeeds
- `retrieval_context_precision_error`: (optional) error message if `retrieval_context_precision` evaluation fails
- `retrieval_context_f1`: (optional) F1 score of the retrieved context with respect to the reference answer, if `retrieval_context_recall` and `retrieval_context_precision` succeed
