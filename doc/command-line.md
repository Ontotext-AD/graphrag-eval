## Command Line Use

To evaluate only correctness of final answers (system responses), you can clone this repository and run the code on the command line:

1. Prepare an input TSV file with columns `Question`, `Reference answer` and `Actual answer`
1. Execute `poetry install --with llm`
1. Execute `OPENAI_API_KEY=<your_api_key> poetry run answer-correctness -i <input_file.tsv> -o <output_file.tsv>`

We plan to improve CLI support in future releases.
