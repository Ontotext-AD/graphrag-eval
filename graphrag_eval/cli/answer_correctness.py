from __future__ import annotations

import argparse
import asyncio
import csv
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

from tqdm import tqdm

from graphrag_eval import llm_factory
from graphrag_eval.answer_correctness import AnswerCorrectnessEvaluator
from graphrag_eval.evaluation import Config

if TYPE_CHECKING:
    from ragas.llms.base import InstructorBaseRagasLLM


def parse_args() -> argparse.Namespace:
    parser = ArgumentParser(
        description="Calculates answer correctness over the entries from the "
                    "input tsv file and stores the output in the output tsv "
                    "file.",
    )
    parser.add_argument(
        "-i",
        "--input-tsv-file-path",
        type=Path,
        required=True,
        help="Input tsv file path with columns `Question`, `Reference answer` "
             "and `Actual answer`",
    )
    parser.add_argument(
        "-o",
        "--output-tsv-file-path",
        type=Path,
        required=True,
        help="Output tsv file path with columns `#Reference`, `#PTarget`, "
             "`#Matching`, `Reasoning`, `Error`",
    )
    parser.add_argument(
        "-c",
        "--config-yaml-file-path",
        type=Path,
        required=True,
        help="Config yaml file path with definition of the LLM to use and "
             "optionally a custom prompt.",
    )
    return parser.parse_args()


async def evaluate_and_write(
    input_tsv_file_path: Path,
    output_tsv_file_path: Path,
    evaluator: AnswerCorrectnessEvaluator,
) -> None:
    csv.field_size_limit(sys.maxsize)

    with open(input_tsv_file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = [row for row in reader]
    print(f"Writing results to {output_tsv_file_path}")
    output_tsv_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_tsv_file_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(
            ["#Reference", "#PTarget", "#Matching", "Reasoning", "Error"]
        )

        for row in tqdm(rows):
            if "Question" not in row or \
                "Reference answer" not in row or \
                "Actual answer" not in row:
                raise ValueError("Unexpected input format!")

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


def run(
    config_yaml_file_path: Path,
    input_tsv_file_path: Path,
    output_tsv_file_path: Path,
):
    config = Config.parse(config_yaml_file_path)
    ragas_llm: InstructorBaseRagasLLM | None = llm_factory.create_llm(
        config.llm
    )
    if ragas_llm is None:
        raise ValueError(
            "LLM must be configured to calculate the answer correctness!"
        )
    if config.answer_correctness and not config.answer_correctness.enabled:
        raise ValueError(
            "Can't disable answer correctness, when running this script!"
        )
    evaluator = AnswerCorrectnessEvaluator(
        ragas_llm=ragas_llm,
        config=config.answer_correctness,
    )
    asyncio.run(evaluate_and_write(
        input_tsv_file_path,
        output_tsv_file_path,
        evaluator,
    ))


def main():
    args = parse_args()
    run(
        args.config_yaml_file_path,
        args.input_tsv_file_path,
        args.output_tsv_file_path,
    )
