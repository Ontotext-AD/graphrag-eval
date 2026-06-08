# Installation

Choose a tier below.

## Basic (no LLM)

Evaluates steps of types:
- SPARQL query
- time series
- data points

Install using pip:

```bash
pip install graphrag-eval
```

or add the following dependency in your `pyproject.toml` file:

```toml
graphrag-eval = "*"
```

## Full

Includes metrics that use an LLM ([§ Metrics using LLM](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/llm.md)):
- answer relevance
- answer correctness
- retrieval steps
- [custom metrics](https://github.com/Ontotext-AD/graphrag-eval/blob/main/docs/custom.md)

Install with the `llm` extra. Using pip:

```bash
pip install 'graphrag-eval[llm]'
```

or add the following dependency in your `pyproject.toml` file:

```toml
graphrag-eval = {version = "*", extras = ["llm"]}
```
