#### Aggregates Keys

The `aggregates` object provides aggregated evaluation metrics. These aggregates support analysis of agent quality, token efficiency, and execution performance. Aggregates are computed:
1. per question template, and
1. over all questions in the dataset, using micro and macro averaging

Aggregates are:
- `per_template`: a dictionary mapping a template identifier to the following statistics:
  - `number_of_error_samples`: number of questions for this template, which resulted in error response
  - `number_of_success_samples`: number of questions for this template, which resulted in successful response
  - `sum`, `mean`, `median`, `min` and `max` statistics for the following metrics over all questions of this template for which the metrics exist:
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
    - `steps`: includes:
      - `total`: for each step type how many times it was executed
      - `once_per_sample`: how many times each step was executed, counted only once per question
      - `empty_results`: how many times the step was executed and returned empty results
      - `errors`: how many times the step was executed and resulted in error
- `micro`: statistics across questions, regardless of template. It includes:
  - `number_of_error_samples`: total number of questions, which resulted in error response
  - `number_of_success_samples`: total number of questions, which resulted in successful response
  - `steps`: includes:
    - `total`: for each step type how many times it was executed
    - `once_per_sample`: how many times each step was executed, counted only once per question
    - `empty_results`: how many times the step was executed and returned empty results
    - `errors`: how many times the step was executed and resulted in error
  - `sum`, `mean`, `median`, `min` and `max` statistics for the following metrics, over all questions where the metrics exist:
    - `input_tokens`
    - `output_tokens`
    - `total_tokens`
    - `elapsed_sec`
    - `answer_recall`
    - `answer_precision`
    - `answer_f1`
    - `answer_relevance`
    - `answer_relevance_cost`
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
  - `answer_relevance_cost`
  - `retrieval_answer_recall`
  - `retrieval_answer_precision`
  - `retrieval_answer_f1`
  - `retrieval_context_recall`
  - `retrieval_context_precision`
  - `retrieval_context_f1`
  - `steps_score`

#### Example Aggregates

```yaml
per_template:
  list_all_transformers_within_Substation_SUBSTATION:
    number_of_error_samples: 0
    number_of_success_samples: 10
    answer_recall:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_precision:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_f1:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_relevance:
      min: 0.9
      max: 0.9
      mean: 0.9
      median: 0.9
      sum: 0.9
    answer_relevance_cost:
      min: 0.0007
      max: 0.0007
      mean: 0.0007
      median: 0.0007
      sum: 0.0007
    steps:
      total:
        autocomplete_search: 10
        sparql_query: 8
      once_per_sample:
        autocomplete_search: 10
        sparql_query: 8
      empty_results:
        autocomplete_search: 2
    steps_score:
      sum: 8
      mean: 0.8
      median: 1
      min: 0
      max: 1
    input_tokens:
      sum: 2064559
      mean: 206455.9
      median: 221263.5
      min: 147171
      max: 221339
    output_tokens:
      sum: 1555
      mean: 155.5
      median: 177
      min: 46
      max: 212
    total_tokens:
      sum: 2066114
      mean: 206611.4
      median: 221439.5
      min: 147217
      max: 221551
    elapsed_sec:
      sum: 259.2278094291687
      mean: 25.92278094291687
      median: 9.677194952964783
      min: 5.529741525650024
      max: 55.4010910987854
  list_all_substations_within_bidding_zone_REGION:
    number_of_error_samples: 0
    number_of_success_samples: 10
    answer_recall:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_precision:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_f1:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_relevance:
      min: 0.9
      max: 0.9
      mean: 0.9
      median: 0.9
      sum: 0.9
    answer_relevance_cost:
      min: 0.0007
      max: 0.0007
      mean: 0.0007
      median: 0.0007
      sum: 0.0007
    steps:
      total:
        autocomplete_search: 10
      once_per_sample:
        autocomplete_search: 10
      empty_results:
        autocomplete_search: 10
    steps_score:
      sum: 0
      mean: 0
      median: 0
      min: 0
      max: 0
    input_tokens:
      sum: 1471880
      mean: 147188
      median: 147188
      min: 147188
      max: 147188
    output_tokens:
      sum: 571
      mean: 57.1
      median: 57
      min: 56
      max: 61
    total_tokens:
      sum: 1472451
      mean: 147245.1
      median: 147245
      min: 147244
      max: 147249
    elapsed_sec:
      sum: 185.5483124256134
      mean: 18.55483124256134
      median: 8.886059165000916
      min: 2.8653159141540527
      max: 47.51542258262634
  list_all_substations_that_are_connected_via_an_ac_line_or_a_dc_line_to_substation_named_SUBSTATION:
    number_of_error_samples: 1
    number_of_success_samples: 9
    answer_recall:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_precision:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_f1:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_relevance:
      min: 0.9
      max: 0.9
      mean: 0.9
      median: 0.9
      sum: 0.9
    answer_relevance_cost:
      min: 0.0007
      max: 0.0007
      mean: 0.0007
      median: 0.0007
      sum: 0.0007
    steps:
      total:
        autocomplete_search: 9
        sparql_query: 17
      once_per_sample:
        autocomplete_search: 9
        sparql_query: 9
      errors:
        sparql_query: 8
    steps_score:
      sum: 9
      mean: 1
      median: 1
      min: 1
      max: 1
    input_tokens:
      sum: 2601595
      mean: 289066.1111111111
      median: 297059
      min: 222528
      max: 298028
    output_tokens:
      sum: 6066
      mean: 674
      median: 700
      min: 363
      max: 805
    total_tokens:
      sum: 2607661
      mean: 289740.1111111111
      median: 297759
      min: 222891
      max: 298787
    elapsed_sec:
      sum: 354.82168316841125
      mean: 39.42463146315681
      median: 41.88556528091431
      min: 26.418761014938354
      max: 52.42662525177002
  list_all_ac_lines_that_traverse_bidding_zones_REGION1_and_REGION2:
    number_of_error_samples: 0
    number_of_success_samples: 10
    answer_recall:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_precision:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_f1:
      sum: 1.0
      mean: 1.0
      median: 1.0
      min: 1.0
      max: 1.0
    answer_relevance:
      min: 0.9
      max: 0.9
      mean: 0.9
      median: 0.9
      sum: 0.9
    answer_relevance_cost:
      min: 0.0007
      max: 0.0007
      mean: 0.0007
      median: 0.0007
      sum: 0.0007
    steps:
      total:
        autocomplete_search: 20
      once_per_sample:
        autocomplete_search: 10
      empty_results:
        autocomplete_search: 20
    steps_score:
      sum: 0
      mean: 0
      median: 0
      min: 0
      max: 0
    input_tokens:
      sum: 1472540
      mean: 147254
      median: 147254
      min: 147254
      max: 147254
    output_tokens:
      sum: 1052
      mean: 105.2
      median: 105
      min: 105
      max: 107
    total_tokens:
      sum: 1473592
      mean: 147359.2
      median: 147359
      min: 147359
      max: 147361
    elapsed_sec:
      sum: 197.44370341300964
      mean: 19.744370341300964
      median: 18.030158162117004
      min: 15.56333041191101
      max: 26.422670125961304
micro:
  number_of_error_samples: 1
  number_of_success_samples: 39
  answer_recall:
    sum: 1.0
    mean: 1.0
    median: 1.0
    min: 1.0
    max: 1.0
  answer_precision:
    sum: 1.0
    mean: 1.0
    median: 1.0
    min: 1.0
    max: 1.0
  answer_f1:
    sum: 1.0
    mean: 1.0
    median: 1.0
    min: 1.0
    max: 1.0
  answer_relevance:
    min: 0.9
    max: 0.9
    mean: 0.9
    median: 0.9
    sum: 0.9
  answer_relevance_cost:
    min: 0.0007
    max: 0.0007
    mean: 0.0007
    median: 0.0007
    sum: 0.0007
  steps_score:
    sum: 17
    mean: 0.4358974358974359
    median: 0
    min: 0
    max: 1
  input_tokens:
    sum: 7610574
    mean: 195142.92307692306
    median: 147254
    min: 147171
    max: 298028
  output_tokens:
    sum: 9244
    mean: 237.02564102564102
    median: 105
    min: 46
    max: 805
  total_tokens:
    sum: 7619818
    mean: 195379.94871794872
    median: 147359
    min: 147217
    max: 298787
  elapsed_sec:
    sum: 997.041508436203
    mean: 25.565166882979565
    median: 18.32871961593628
    min: 2.8653159141540527
    max: 55.4010910987854
macro:
  answer_recall:
    mean: 1.0
  answer_precision:
    mean: 1.0
  answer_f1:
    mean: 1.0
  answer_relevance:
    mean: 0.9
  answer_relevance_cost:
    mean: 0.0007
  steps_score:
    mean: 0.45
  input_tokens:
    mean: 197491.0027777778
  output_tokens:
    mean: 247.95
  total_tokens:
    mean: 197738.9527777778
  elapsed_sec:
    mean: 25.911653497483996
```
