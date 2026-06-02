import argparse
import asyncio
import csv
from argparse import ArgumentParser
from pathlib import Path

from tqdm import tqdm

from graphrag_eval import llm_factory
from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator
from graphrag_eval.evaluation import Config


def parse_args() -> argparse.Namespace:
    parser = ArgumentParser()
    parser.add_argument("-i", "--in-file", type=str, required=True)
    parser.add_argument("-o", "--out-file", type=str, required=True)
    parser.add_argument("-c", "--config-path", type=Path, required=True)
    return parser.parse_args()


async def evaluate_and_write(
    in_file_path: str | Path,
    out_file_path: str | Path,
    evaluator: AnswerCorrectnessEvaluator,
) -> None:
    with open(in_file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = [row for row in reader]
    print(f"Writing results to {out_file_path}")
    Path(out_file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_file_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["#Reference", "#PTarget", "#Matching", "Reasoning", "Error"])
        for row in tqdm(rows):
            try:
                vals = await evaluator.evaluate_answer(
                    row["Question"],
                    row["Reference answer"],
                    row["Actual answer"]
                )
                vals = vals + ("",)
                writer.writerow(vals)
            except Exception as exc:
                writer.writerow(["", "", "", "", str(exc)])
            f.flush()


def main():
    args = parse_args()
    config = Config.parse(args.config_path)
    ragas_llm = llm_factory.create_llm(config)
    if ragas_llm is None:
        raise ValueError("LLM must be configured to calculate the answer correctness!")
    else:
        evaluator = AnswerCorrectnessEvaluator(llm=ragas_llm)
        asyncio.run(evaluate_and_write(
            args.in_file,
            args.out_file,
            evaluator,
        ))
