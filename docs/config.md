# Configuration

The configuration has two sections: `llm` and `custom_evaluation`:

* `llm`: required for [LLM-based metrics](https://github.com/Ontotext-AD/graphrag-eval/docs/llm.md). The
  following keys are required:
    * `generation`: required. The following keys are required:
        * `provider`: (str) name of the organization providing the generation
          model, as supported by LiteLLM
        * `model`: (str) name of the generation model
        * `temperature`: (float in the range [0.0, 2.0]) adversarial
          temperature for generation
        * `max_tokens`: (int > 0) maximum number of tokens to generate
        * Optional keys: parameters to be passed to LiteLLM for generation (for
          [`answer_correctness`](https://github.com/Ontotext-AD/graphrag-eval/docs/output.md) and
          [custom evaluation](https://github.com/Ontotext-AD/graphrag-eval/docs/custom.md)). Examples:
          * `base_url`: (str) base URL for the generation model, alternative
            to the provider's default URL
          * `api_key`: (str) API key for the generation model, alternative to
            setting the environment variable corresponding to the provider (e.g.
            `OPENAI_API_KEY` for OpenAI)
    * `embedding`: required for [`answer_relevance`](https://github.com/Ontotext-AD/graphrag-eval/docs/output.md).
        * `provider`: (str) name of the organization providing the embedding
          model
        * `model`: (str) name of the embedding model
* `custom_evaluations`: (list of the following maps) required nonempty for
[custom evaluation](https://github.com/Ontotext-AD/graphrag-eval/docs/custom.md). Each map has keys:
    * `name`: (str) name of the evaluation
    * `inputs`: (list[str]) list of input variables. Any combination of the
      following:
        * `question`
        * `reference_answer`
        * `reference_steps`
        * `actual_answer`
        * `actual_steps`
    * `steps_keys`: (list[str]; required if `inputs` contains `actual_steps` or
      `reference_steps`) one or both of:
        * `args`
        * `output`
    * `steps_name`: (str; required if `inputs` contains `actual_steps` or
      `reference_steps`) the type (name) of steps to include in the evaluation
    * `instructions`: (str) instructions for the evaluation
    * `outputs`: (map[str]) output variable names and descriptions

## Example configuration file with LLM configuration

Below is a YAML file that configures the LLM generation (for
[metrics that require an LLM](https://github.com/Ontotext-AD/graphrag-eval/docs/llm.md)) and embedding (for
[`answer_relevance`](https://github.com/Ontotext-AD/graphrag-eval/docs/output.md)). It assumes that the environment
variable `OPENAI_API_KEY` is set with your OpenAI API key.

```YAML
llm:
  generation:
    provider: openai
    model: gpt-4o-mini
    temperature: 0.0
    max_tokens: 65536
  embedding:
    provider: openai
    model: text-embedding-3-small
```

## Example configuration file with LLM configuration and API keys

Below is a YAML file that configures the LLM generation (for
[metrics that require an LLM](https://github.com/Ontotext-AD/graphrag-eval/docs/llm.md)) and embedding (for
[`answer_relevance`](https://github.com/Ontotext-AD/graphrag-eval/docs/metrics.md)) with different API keys in place of
environment variables.

```YAML
llm:
  generation:
    provider: azure
    model: graphrag-eval-system-tests-gpt-5.2
    base_url: https://my-generator.openai.azure.com
    temperature: 0.0
    max_tokens: 8192
    api_key: ...
  embedding:
    provider: azure
    model: graphrag-eval-system-tests-text-embedding-3-small
    api_base: https://my-embedder.openai.azure.com
    api_key: ...
```

## Example configuration file with custom evaluations

Below is a YAML file that defines two custom evaluations:
1. a simple relevance evaluation
1. a SPARQL retrieval evaluation using the reference answer

This is an example of the format and may not create accurate evaluations.

```YAML
llm:
  generation:
    provider: openai
    model: gpt-4o-mini
    temperature: 0.0
    max_tokens: 65536
  embedding:
    provider: openai
    model: text-embedding-3-small
custom_evaluations:
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
