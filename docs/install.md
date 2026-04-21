# Installation

To evaluate only steps:
```bash
pip install graphrag-eval
```
or add the following dependency in your `pyproject.toml` file:
```toml
graphrag-eval = "*"
```

To evaluate `answer_relevance`, answer correctness metrics (`answer_recall`, `answer_precision`, `answer_f1`) (see [§ LLM use in evaluation](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/llm.md)) or [custom metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/custom.md) install the `llm` extra:

```bash
pip install 'graphrag-eval[llm]'
```

or add the following dependency in your `pyproject.toml` file:
```toml
graphrag-eval = {version = "*", extras = ["llm"]}
```
