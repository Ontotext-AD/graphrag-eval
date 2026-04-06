# Metrics

The library computes metrics for the quality of the answers. The groups of possible metrics are:
1. **[RAGAS answer relevance](https://docs.ragas.io/en/v0.4.3/concepts/metrics/available_metrics/answer_relevance/)** (`answer_relevance`)
1. **Answer correctness**: recall, precision, F1 of claims extracted from the actual answer with respect to reference answer claims (`answer_recall`, `answer_precision`, `answer_f1`)
1. **Steps score**: correctness of the agent's steps in responding to a user query (`steps_score`) ([§ Steps score](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/steps.md#steps-score))
1. Vector retrieval
    1. **Answer reference**: Recall, precision, F1 of the retrieved context claims with respect to the reference answer claims (`retrieval_answer_recall`, `retrieval_answer_precision`, `retrieval_answer_f1`)
    1. **Context reference**: Recall, precision, F1 of the retrieved context claims with respect to the reference context claims (`retrieval_context_recall`, `retrieval_context_precision`, `retrieval_context_f1`)
    1. **Chunk IDs**: Recall, precision, F1 of retrieved chunk IDs with respect to the reference chunk IDs (`retrieval_chunk_ids_recall`, `retrieval_chunk_ids_precision`, `retrieval_chunk_ids_f1`) ([§ Retrieval evaluation using chunk IDs](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/retrieval-ids.md))
1. **Aggregates**: min, max, sum, mean, median of the above metrics ([§ Aggregate metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/output.md#aggregate-metrics))
1. *Custom metrics* defined by the user ([§ Custom evaluation](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/custom.md))

Each metric has required reference and target data types; it is computed if those data are among the supplied reference answer data and the actual answer data. The output for each question includes keys for metrics and other data, listed in [§ Output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/output.md).
