# Installation

To evaluate only steps:
```bash
pip install graphrag-eval
```
or add the following dependency in your `pyproject.toml` file:
```toml
graphrag-eval = "*"
```

To evaluate `answer_relevance` and answer correctness metrics (`answer_recall`, `answer_precision`, `answer_f1`) (see section [Metrics](https://github.com/Ontotext-AD/graphrag-eval/docs/metrics.md)) or use a [custom evaluation](https://github.com/Ontotext-AD/graphrag-eval/docs/custom.md):

```bash
pip install 'graphrag-eval[llm]'
```

or add the following dependency in your `pyproject.toml` file:
```toml
graphrag-eval = {version = "*", extras = ["llm"]}
```
