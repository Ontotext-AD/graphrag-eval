import json
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path
from statistics import mean, median
from typing import Any, Collection, Iterable


METRICS = [
    "answer_recall",
    "answer_precision",
    "answer_relevance",
    "answer_relevance_cost",
    "answer_f1",
    "steps_score",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "elapsed_sec"
]
STEPS_METRICS = {
    "retrieval": [
        "retrieval_answer_precision",
        "retrieval_answer_precision_cost",
        "retrieval_answer_recall",
        "retrieval_answer_recall_cost",
        "retrieval_answer_f1",
        "retrieval_answer_f1_cost",
        "retrieval_context_precision",
        "retrieval_context_precision_cost",
        "retrieval_context_recall",
        "retrieval_context_recall_cost",
        "retrieval_context_f1",
        "retrieval_context_f1_cost",
    ]
}
RETAINED_METRICS = [
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "elapsed_sec"
]


def stats_for_series(values: Iterable[int | float]) -> dict[str, float]:
    return {
        "sum": sum(values),
        "mean": mean(values) if values else 0,
        "median": median(values) if values else 0,
        "min": min(values) if values else 0,
        "max": max(values) if values else 0,
    }


def update_step_metrics(
    sample: dict[str, Any],
    template_step_metrics: dict[str, list[float]],
):
    for step in sample.get("actual_steps", []):
        for metric in STEPS_METRICS.get(step["name"], []):
            value = step.get(metric)
            if value is not None:
                template_step_metrics[metric].append(value)


def update_stats(
    sample: dict[str, float | int],
    template_stats: dict[str, list[float | int]],
    custom_metrics: list[str] = [],
):
    for metric in METRICS + custom_metrics:
        value = sample.get(metric)
        if isinstance(value, (float, int)):
            template_stats[metric].append(value)


def update_steps_summary(
    sample: dict[str, Any],
    template_steps_summary: dict,
):
    seen = set()
    for step in sample.get("actual_steps", []):
        name = step["name"]
        template_steps_summary["total"][name] += 1
        if step["status"] == "error":
            template_steps_summary["errors"][name] += 1
        if name not in seen:
            seen.add(name)
            template_steps_summary["once_per_sample"][name] += 1
        if step["status"] != "error":
            try:
                res = json.loads(step["output"])
                if isinstance(res, dict) and "results" in res and "bindings" in res["results"]:
                    if not res["results"]["bindings"]:
                        template_steps_summary["empty_results"][name] += 1
            except json.decoder.JSONDecodeError:
                pass


def compute_per_template_stats(
    templates_ids: Collection[str],
    number_of_samples_per_template_by_status: dict[str, dict[str, int]],
    stats_per_template: dict[str, dict[str, Sequence[int]]],
    steps_summary_per_template: dict[str, dict[str, dict[str, int]]],
    step_metrics_per_template: dict[str, dict[str, Sequence[int]]],
    custom_metrics: list[str] = [],
) -> dict[str, dict[str, Any]]:
    summary = {}

    # Add per-template stats
    for template_id in templates_ids:
        n_by_status = number_of_samples_per_template_by_status[template_id]
        summary[template_id] = {
            "number_of_error_samples": n_by_status["error"],
            "number_of_success_samples": n_by_status["success"],
        }
        for metric in METRICS + custom_metrics:
            series = stats_per_template[template_id].get(metric, [])
            if series or metric in RETAINED_METRICS:
                summary[template_id][metric] = stats_for_series(series)
        steps_summary = {
            k1: {k2: v2 for k2, v2 in v1.items()}
            for k1, v1 in steps_summary_per_template[template_id].items()
        }
        if steps_summary:
            summary[template_id]["steps"] = steps_summary

        # Add step metrics for the template
        template_step_metrics = {}
        for metric, values in step_metrics_per_template[template_id].items():
            template_step_metrics[metric] = stats_for_series(values)
        if template_step_metrics:
            summary[template_id]["steps"].update(template_step_metrics)
    return summary


def compute_micro_stats(
    number_of_samples_per_template_by_status: dict[str, dict[str, int]],
    stats_per_template: dict[str, dict[str, Sequence[int]]],
    steps_summary_per_template: dict[str, dict[str, dict[str, int]]],
    step_metrics_per_template: dict[str, dict[str, Sequence[int]]],
    custom_metrics: list[str] = []
) -> dict:
    values = number_of_samples_per_template_by_status.values()
    micro_summary = defaultdict(dict, {
        "number_of_error_samples": sum(v["error"] for v in values),
        "number_of_success_samples": sum(v["success"] for v in values)
    })
    for metric in METRICS + custom_metrics:
        series = [
            i
            for values in stats_per_template.values()
            for i in values[metric]
            if values.get(metric) is not None
        ]
        if series or metric in RETAINED_METRICS:
            micro_summary[metric] = stats_for_series(series)

    # Add micro step metrics
    micro_step_metrics = defaultdict(list)
    for template_metrics in step_metrics_per_template.values():
        for metric, values in template_metrics.items():
            micro_step_metrics[metric].extend(values)
    for metric, values in micro_step_metrics.items():
        micro_summary[metric] = stats_for_series(values)

    steps_summary = defaultdict(lambda: defaultdict(int))
    for template_steps_summary in steps_summary_per_template.values():
        for summary_name, steps_stats in template_steps_summary.items():
            for step_id, count in steps_stats.items():
                steps_summary[summary_name][step_id] += count
    steps_summary = {k: dict(v) for k, v in steps_summary.items()}
    if len(steps_summary) > 0:
        micro_summary["steps"] = steps_summary

    return dict(micro_summary)


def compute_macro_stats(
    summary_per_template: dict[str, dict[str, dict[str, Any]]]
) -> dict:
    macro_summary = defaultdict(dict)
    for metric in METRICS:
        means = [
            values[metric]["mean"]
            for values in summary_per_template.values()
            if values.get(metric) is not None
        ]
        if means or metric in RETAINED_METRICS:
            macro_summary[metric]["mean"] = mean(means or [0])

    # Add macro step metrics
    macro_step_metrics = defaultdict(list)
    for template_summary in summary_per_template.values():
        for metric, stats in template_summary.get("steps", {}).items():
            if "mean" in stats:
                macro_step_metrics[metric].append(stats["mean"])
    for metric, values in macro_step_metrics.items():
        macro_summary[metric]["mean"] = mean(values or [0])
    return dict(macro_summary)


def compute_aggregates(
    samples: list[dict],
    custom_eval_config_file_path: str | Path | None = None,
) -> dict:
    number_of_samples_per_template_by_status = defaultdict(lambda: defaultdict(int))
    stats_per_template = defaultdict(lambda: defaultdict(list))
    steps_summary_per_template = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    step_metrics_per_template = defaultdict(lambda: defaultdict(list))
    custom_metrics = []
    if custom_eval_config_file_path:
        from .custom_evaluation import parse_config
        evaluators = parse_config(custom_eval_config_file_path)
        custom_metrics = [m for e in evaluators for m in e.output_variables]

    # Compute per-template stats
    templates_ids = set()
    for sample in samples:
        template_id = sample["template_id"]
        templates_ids.add(template_id)

        if "error" in sample:
            number_of_samples_per_template_by_status[template_id]["error"] += 1
        else:
            number_of_samples_per_template_by_status[template_id]["success"] += 1
        update_stats(sample, stats_per_template[template_id], custom_metrics)
        update_steps_summary(sample, steps_summary_per_template[template_id])
        update_step_metrics(sample, step_metrics_per_template[template_id])

    summary = {
        "per_template": compute_per_template_stats(
            templates_ids,
            number_of_samples_per_template_by_status,
            stats_per_template,
            steps_summary_per_template,
            step_metrics_per_template,
            custom_metrics,
        ),
        "micro": compute_micro_stats(
            number_of_samples_per_template_by_status,
            stats_per_template,
            steps_summary_per_template,
            step_metrics_per_template,
            custom_metrics,
        )
    }
    summary["macro"] = compute_macro_stats(summary["per_template"])
    return summary
