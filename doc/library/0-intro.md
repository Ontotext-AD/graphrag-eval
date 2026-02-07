## Use as a Library

To evaluate answers and/or steps:
1. Install this package: section [Install](https://github.com/Ontotext-AD/graphrag-eval/blob/main/installation.md)
1. Format the dataset of questions and reference answers and/or steps: section [Reference Q&A Data](https://github.com/Ontotext-AD/graphrag-eval/blob/main/reference-data.md)
1. Format the answers and/or steps you want to evaluate: section [Responses to evaluate](https://github.com/Ontotext-AD/graphrag-eval/blob/main/target-data.md)
1. To evaluate answer relevance:
    1. Include `actual_answer` in the target data to evaluate
    1. Set environment variable `OPENAI_API_KEY` appropriately
1. To evaluate answer correctness:
    1. Include `reference_answer` in the reference dataset and `actual_answer` in the target data to evaluate
    1. Set environment variable `OPENAI_API_KEY` appropriately
1. To evaluate steps:
    1. Include `reference_steps` in the reference data and `actual_steps` in target data to evaluate
1. Call the evaluation function with the reference data and target data: section [Usage Code](https://github.com/Ontotext-AD/graphrag-eval/blob/main/example-usage-code.md)
1. Call the aggregation function with the evaluation results: section [Usage Code](https://github.com/Ontotext-AD/graphrag-eval/blob/main/example-usage-code.md)

Answer evaluation (correctness and relevance) and [custom evaluation](https://github.com/Ontotext-AD/graphrag-eval/blob/main/custom-evaluation.md) use the LLM `openai/gpt-4o-mini`.
