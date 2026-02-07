### Usage Code

```python
from graphrag_eval import run_evaluation, compute_aggregates

reference_qas: list[dict] = [] # read your reference data
chat_responses: dict = {} # call your implementation to get the response
evaluation_results = run_evaluation(reference_qas, chat_responses)
aggregates = compute_aggregates(evaluation_results)
```

`evaluation_results` is a list of statistics for each question, as in section [Evaluation Results](https://github.com/Ontotext-AD/graphrag-eval/blob/main/evaluation-output.md). The format is explained in section [Output Keys](https://github.com/Ontotext-AD/graphrag-eval/blob/main/output-keys.md)

If your chat responses contain actual answers, set your environment variable `OPENAI_API_KEY` before running the code above.
