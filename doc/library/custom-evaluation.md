### Custom Evaluation (Custom Metrics)

You (the user) can define your own metrics of system outputs to be evaluated
using an LLM. To do this, specify its name, inputs, outputs and instructions in
a YAML file and pass the file path as a parameter to `run_evaluation()`. This 
will return your output metrics alongside the standard metrics described 
in previous sections.

One configuration file can define multiple custom evaluations, each of which
will be done as a separate query to the LLM. Each evaluation can have multiple 
outputs. The format is shown in the example sections below.

#### Example Custom Evaluation Configuration File

Below is a YAML file that defines two custom evaluations:
1. a simple relevance evaluation
1. a SPARQL retrieval evaluation using the reference answer

This is an example of the format and may not create accurate evaluations.

```YAML
-
  name: my_answer_relevance
  inputs:
    - question
    - actual_answer
  instructions: |
    Evaluate how relevant is the answer to the question.
  outputs:
    my_answer_relevance: fraction between 0 and 1
    my_answer_relevance_reason: reason for your evaluation
-
  name: sparql_llm_evaluation
  inputs:
    - question
    - reference_answer
    - actual_steps
  steps_keys:
    - output
  steps_name: sparql
  instructions: |
    Divide the reference answer into claims and try to match each claim to the
    SPARQL query results. Count the:
    - reference claims
    - SPARQL results
    - matching claims
  outputs:
    sparql_recall: Number of matching claims as a fraction of reference claims (fraction 0-1)
    sparql_precision: Number of matching claims as a fraction of SPARQL results (fraction 0-1)
    sparql_reason: reason for your evaluation
```

#### Example Call to Evaluate Using Custom Metrics

```python
evaluation_results = run_evaluation(
    reference_qa_dataset, 
    chat_responses, 
    "my_project/custom_eval.yaml"
)
```

#### Example Output for Custom SPARQL Evaluation 

With the 
[custom SPARQL evaluation](example-custom-evaluation-configuration-file),
the output is as for section [Evaluation Results](#evaluation-results), except
that it has the following additional keys and example values:

```yaml
  my_answer_relevance: 0.9
  my_answer_relevance_eval_reason: The answer contains relevant information except for the sentence about total revenue
  sparql_recall: 0.75
  sparql_precision: 0.6
  sparql_eval_reason: The reference answer has 4 claims; there are 5 SPARQL results; 3 claims match
```

#### Output in Case of Evaluation Error

If there is an error during evaluation, the output will have `null` for all
custom evaluation specified output keys and will have an additional key 
explaining the error. The key will be `{name}_error` where `name` is the custom
evaluation name.

There are three types of errors:
1. The reference input is missing keys requested in the custom evaluation 
configuration. Example: 
`custom_1_error: Reference missing key 'reference_steps'`
1. The actual output to be evaluated is missing keys requested in the custom
evaluation configuration.  Example: 
`custom_1_error: Actual output missing 'actual_steps'`
1. The evaluating LLM output does not conform to the custom evaluation 
configuration. Example: 
`custom_1_error: "Expected 6 tab-separated values, got: 0.1\tCustom answer reason"`

#### Recommendations for Custom Evaluations

1. Specify only several outputs in each evaluation
1. Request an explanation output for output quantities you ask the LLM to count
or estimate. You can ask for one explanation per quantity or one shared 
explanation for 2-3 quantities
