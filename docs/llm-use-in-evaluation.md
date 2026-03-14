# LLM use in evaluation

The following metrics use an LLM which must be configured using a
[configuration](configuration.md) file:
* answer metrics
  * `answer_recall`
  * `answer_precision`
  * `answer_f1`
  * `answer_relevance`
* retrieval context metrics:
  * `retrieval_answer_recall`
  * `retrieval_answer_precision`
  * `retrieval_answer_f1`
  * `retrieval_context_recall`
  * `retrieval_context_precision`
  * `retrieval_context_f1`
* [custom evaluation](custom-evaluation.md)

Supported LLMs are all those supported by the
[`litellm`](https://github.com/BerriAI/litellm) library, including all major
LLMs and local models via Ollama.

If no LLM is configured or the `config_file_path` parameter is not provided,
these metrics are not evaluated.
