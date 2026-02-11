## Installation

To evaluate only steps:
```bash
pip install graphrag-eval
```
or add the following dependency in your `pyproject.toml` file:
```toml
graphrag-eval = "*"
```

To evaluate answer relevance and answer correctness or use a [custom evaluation](custom-evaluation.md):

```bash
pip install 'graphrag-eval[llm]'
```

or add the following dependency in your `pyproject.toml` file:
```toml
graphrag-eval = {version = "*", extras = ["llm"]}
```
