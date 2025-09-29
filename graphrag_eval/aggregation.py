import json
from collections import defaultdict
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
PROTECTED_METRICS = [
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


def update_step_metrics_per_template(
    sample: dict,
    step_metrics_per_template: dict,
    template_id: str
):
    for step in sample.get("actual_steps", []):
        if step["name"] in STEPS_METRICS:
            for metric in STEPS_METRICS[step["name"]]:
                value = step.get(metric)
                if value is not None:
                    step_metrics_per_template[template_id][metric].append(value)


def update_stats_per_template(
    sample: dict,
    stats_per_template: dict,
    template_id: str
):
    for metric in METRICS:
        value = sample.get(metric)
        if value is not None:
            stats_per_template[template_id][metric].append(value)


def update_steps_summary_per_template(
    sample: dict,
    steps_summary_per_template: dict,
    template_id: str
):
    seen = set()
    for step in sample.get("actual_steps", []):
        name = step["name"]
        template_steps_summary = steps_summary_per_template[template_id]
        template_steps_summary["total"][name] += 1
        if step["status"] == "error":
            template_steps_summary["errors"][name] += 1
        if name not in seen:
            seen.add(name)
            template_steps_summary["once_per_sample"][name] += 1

        if step["status"] != "error":
            try:
                res = json.loads(step["output"])
                if "results" in res and "bindings" in res["results"]:
                    if not res["results"]["bindings"]:
                        template_steps_summary["empty_results"][name] += 1
            except json.decoder.JSONDecodeError:
                pass


def get_per_template_stats(
    templates_ids: Collection[str],
    number_of_samples_per_template_by_status: dict[str, dict[str, int]],
    steps_summary_per_template: dict[str, dict[str, dict[str, int]]],
    stats_per_template: dict[str, dict[str, dict[str, int]]],
    step_metrics_per_template: dict[str, dict[str, dict[str, int]]],
) -> dict[str, dict[str, Any]]:
    summary = {}

    # Add per-template stats
    for template_id in templates_ids:
        num_by_status = number_of_samples_per_template_by_status[template_id]
        template_summary: dict[str, Any] = {
            "number_of_error_samples": num_by_status["error"],
            "number_of_success_samples": num_by_status["success"],
        }
        steps_summary = {
            k1: {k2: v2 for k2, v2 in v1.items()}
            for k1, v1 in steps_summary_per_template[template_id].items()
        }
        if steps_summary:
            template_summary.update({"steps": steps_summary})
        for metric in METRICS:
            results_for_template = stats_per_template[template_id]
            series = results_for_template.get(metric, [])
            if series or metric in PROTECTED_METRICS:
                template_summary[metric] = stats_for_series(series)

        # Add step metrics for the template
        template_step_metrics = {}
        for metric, values in step_metrics_per_template[template_id].items():
            template_step_metrics[metric] = stats_for_series(values)
        if template_step_metrics:
            template_summary["steps"].update(template_step_metrics)

        summary[template_id] = template_summary
    return summary


def compute_micro_stats(
    number_of_samples_per_template_by_status,
    stats_per_template,
    step_metrics_per_template
):
    values_ = number_of_samples_per_template_by_status.values()
    micro_summary = {
        "number_of_error_samples": sum(vals["error"] for vals in values_),
        "number_of_success_samples": sum(vals["success"] for vals in values_),
    }
    for metric in METRICS:
        series = [
            i
            for values in stats_per_template.values()
            for i in values[metric]
            if values.get(metric) is not None
        ]
        if series or metric in PROTECTED_METRICS:
            micro_summary[metric] = stats_for_series(series)

    # Add micro step metrics
    micro_step_metrics = defaultdict(list)
    for template_metrics in step_metrics_per_template.values():
        for metric, values in template_metrics.items():
            micro_step_metrics[metric].extend(values)
    step_metrics = {
        metric: stats_for_series(values)
        for metric, values in micro_step_metrics.items()
    }
    micro_summary.update(step_metrics)
    return micro_summary


def compute_macro_stats(
    summary_per_template: dict[str, dict[str, dict[str, dict[str, float]]]]
) -> dict:
    macro_summary = {}
    for metric in METRICS:
        means = [
            values[metric]["mean"]
            for template_id, values in summary_per_template.items()
            if values.get(metric) is not None
        ]
        print(metric, means)
        if means or metric in PROTECTED_METRICS:
            macro_summary[metric] = {"mean": mean(means) if means else 0}

    # Add macro step metrics
    macro_step_metrics = defaultdict(list)
    for template_id, template_summary in summary_per_template.items():
        if "steps" in template_summary:
            for metric, stats in template_summary["steps"].items():
                if "mean" in stats:
                    macro_step_metrics[metric].append(stats["mean"])
    step_metrics = {
        metric: {"mean": mean(values) if values else 0}
        for metric, values in macro_step_metrics.items()
    }
    macro_summary.update(step_metrics)
    return macro_summary


def compute_aggregates(samples: list[dict]) -> dict:
    number_of_samples_per_template_by_status = defaultdict(lambda: defaultdict(int))
    stats_per_template = defaultdict(lambda: defaultdict(list))
    steps_summary_per_template = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    step_metrics_per_template = defaultdict(lambda: defaultdict(list))

    # Compute per-template stats
    templates_ids = set()
    for sample in samples:
        template_id = sample["template_id"]
        templates_ids.add(template_id)

        if "error" in sample:
            number_of_samples_per_template_by_status[template_id]["error"] += 1
            continue
        number_of_samples_per_template_by_status[template_id]["success"] += 1

        update_stats_per_template(sample, stats_per_template, template_id)
        update_steps_summary_per_template(
            sample,
            steps_summary_per_template,
            template_id
        )
        update_step_metrics_per_template(
            sample,
            step_metrics_per_template,
            template_id
        )

    summary = {}
    summary["per_template"] = get_per_template_stats(
        templates_ids,
        number_of_samples_per_template_by_status,
        steps_summary_per_template,
        stats_per_template,
        step_metrics_per_template
    )
    summary["micro"] = compute_micro_stats(
        number_of_samples_per_template_by_status,
        stats_per_template,
        step_metrics_per_template
    )
    summary["macro"] = compute_macro_stats(summary["per_template"])
    return summary
