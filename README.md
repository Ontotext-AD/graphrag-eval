<p align="center">
  <img alt="Graphwise Logo" src="https://github.com/Ontotext-AD/graphrag-eval/blob/main/.github/Graphwise_Logo.jpg">
</p>

# QA Evaluation

This is a Python library for assessing the quality of question-answering systems such as systems with LLM-based agents. It is agnostic to the agent implementation and LLM it uses.

The evaluation is based on a user-provided reference dataset containing questions, reference answers, and optional reference steps, such as expected tool uses. The evaluator compares these references to the agent's actual answers and executed steps. Reference steps can be grouped to allow some expected steps to occur in any order.

The library provides built-in evaluation metrics and allows the user to define their own (custom) metrics ([§ Metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/metrics.md)).

## Documentation

- [Quickstart](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/quickstart.md)
- [Metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/metrics.md)
- [Configuration](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/config.md)
- [Input](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/input.md)
- [Output](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/output.md)

## Maintainers

Developed and maintained by [Graphwise](https://graphwise.ai/). For issues and feature requests, please open a [GitHub issue](https://github.com/Ontotext-AD/graphrag-eval/issues).

## License

Apache-2.0 License. See the [LICENSE](https://github.com/Ontotext-AD/graphrag-eval/blob/main/LICENSE) file for details.
