# Installation

To evaluate only steps:
```bash
pip install graphrag-eval
```
or add the following dependency in your `pyproject.toml` file:
```toml
graphrag-eval = "*"
```

To evaluate `answer_relevance` and answer correctness metrics (`answer_recall`,
`answer_precision`, `answer_f1`; see section [Output keys](output.md)) or
use a [custom evaluation](custom.md):

```bash
pip install 'graphrag-eval[llm]'
```

or add the following dependency in your `pyproject.toml` file:
```toml
graphrag-eval = {version = "*", extras = ["llm"]}
```
