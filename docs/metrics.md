# Metrics

The library computes metrics for the quality of the answers. The groups of
possible metrics are:
1. `answer_relevance`
1. Metrics of answer correctness
   1. `answer_recall`
   1. `answer_precision`
   1. `answer_f1`
1. `steps_score`: an overall metric of the correctness of the steps the agent
   executed in response to the user's query (see section
   [Steps score](steps.md#steps-score))
1. Metrics of vector retrieval quality, computed for reference retrieval steps
   matched with actual retrieval steps
    1. Retrieval quality using the reference answer 
        1. `retrieval_answer_recall`
        1. `retrieval_answer_precision`
        1. `retrieval_answer_f1`
    1. Retrieval quality using a reference context
        1. `retrieval_context_recall`
        1. `retrieval_context_precision`
        1. `retrieval_context_f1`
    1. Retrieval quality using chunk IDs (section
    [Retrieval evaluation using chunk IDs](retrieval-ids.md))
1. Aggregates min, max, sum, mean, median of the above metrics (section
   [Aggregate metrics](output.md#aggregate-metrics))

Which of these metrics are output depends on the inputs. Specifically, a metric
is computed and output if the types of input required to compute it are
provided in the reference dataset and the responses of the system being
evaluated.

For each question, the output includes keys for those metrics and other data
detailed in section [Output](output.md).

The user can also define their own custom metrics using the configuration file:
see section [Custom evaluation](custom.md)
