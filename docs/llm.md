# LLM use in evaluation

Some metrics use an LLM which must be configured in a [configuration](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/config.md) file. The following metrics require a LLM generation config:
- answer metrics
  - `answer_recall`
  - `answer_precision`
  - `answer_f1`
  - `answer_relevance`: requires both generation config and embedding config
- retrieval quality metrics:
  - `retrieval_answer_recall`
  - `retrieval_answer_precision`
  - `retrieval_answer_f1`
  - `retrieval_context_recall`
  - `retrieval_context_precision`
  - `retrieval_context_f1`
- [custom evaluation](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/custom.md)

Supported LLM providers are all those supported by the [`litellm`](https://github.com/BerriAI/litellm) library, including all major LLMs and local LLMs via Ollama.

The configuration file path must be passed as parameter `config_file_path=` to functions `run_evaluation()` and `compute_aggregates()`. If no LLM is configured or the `config_file_path` parameter is not provided, these metrics are not evaluated.
