import json
from collections import defaultdict
from collections.abc import Sequence
from typing import Any

from .retrieval_context_ids import recall_at_k
from .sparql import compare_sparql_results
from .timeseries import compare_retrieve_time_series, compare_retrieve_data_points

Match = tuple[int, int, int, float]
Step = dict[str, Any]
StepsGroup = Sequence[Step]  # We will index into a group


def compare_steps(reference_step: Step, actual_step: Step) -> float:
    actual_output = actual_step["output"]
    reference_output = reference_step.get("output")
    reference_output_media_type = reference_step.get("output_media_type")

    if reference_output_media_type == "application/sparql-results+json":
        return compare_sparql_results(
            json.loads(reference_output),
            json.loads(actual_output),
            reference_step["required_columns"],
            reference_step.get("ordered", False),
            reference_step.get("ignore_duplicates", True),
        )
    elif reference_output_media_type == "application/json":
        return float(json.loads(reference_output) == json.loads(actual_output))
    elif reference_step["name"] == "retrieval" and reference_output:
        ref_contexts_ids = [c["id"] for c in json.loads(reference_output)]
        act_contexts_ids = [c["id"] for c in json.loads(actual_output)]
        k = actual_step["args"]["k"]
        return recall_at_k(ref_contexts_ids, act_contexts_ids, k)
    elif reference_step["name"] == "retrieve_time_series":
        return compare_retrieve_time_series(reference_step, actual_step)
    elif reference_step["name"] == "retrieve_data_points":
        return compare_retrieve_data_points(reference_step, actual_step, actual_step["execution_timestamp"])
    return float(reference_output == actual_output)


def match_group(
    reference_groups: Sequence[StepsGroup],
    group_idx: int,
    actual_steps: Sequence[Step],
    candidates_by_name: dict[str, list[int]],
) -> list[Match]:
    used_actual_indices = set()
    matches = []

    reference_group = reference_groups[group_idx]
    for reference_idx, reference_step in reversed(list(enumerate(reference_group))):
        name = reference_step["name"]
        candidates = reversed(candidates_by_name.get(name, []))
        for actual_idx in candidates:
            if actual_idx in used_actual_indices:
                continue
            actual_step = actual_steps[actual_idx]
            score = compare_steps(reference_step, actual_step)
            if score > 0.0:
                matches.append((group_idx, reference_idx, actual_idx, score))
                used_actual_indices.add(actual_idx)
                break
    return matches


def collect_possible_matches_by_name_and_status(
    group: StepsGroup,
    actual_steps: Sequence[Step],
    search_upto: int,
) -> dict[str, list[int]]:
    group_by_name = defaultdict(list)

    for j in range(search_upto):
        name = actual_steps[j]["name"]
        if actual_steps[j]["status"] == "success":
            group_by_name[name].append(j)

    reference_names = {step["name"] for step in group}
    return {name: group_by_name[name] for name in reference_names if name in group_by_name}


def get_steps_matches(
    reference_groups: Sequence[StepsGroup],
    actual_steps: Sequence[Step],
) -> list[Match]:
    matches = []
    search_upto = len(actual_steps)
    for group_idx in reversed(range(len(reference_groups))):
        group = reference_groups[group_idx]
        candidates = collect_possible_matches_by_name_and_status(group, actual_steps, search_upto)
        matched = match_group(reference_groups, group_idx, actual_steps, candidates)
        if len(matched) == len(group):
            matches.extend(matched)
            search_upto = min(actual_idx for (_, _, actual_idx, _) in matched)
        elif len(matched) < len(group):
            matches.extend(matched)
            break  # a step is not matched and missing, abort
        else:
            break  # a step is not matched and missing, abort
    return matches


def evaluate_steps(
    reference_steps_groups: Sequence[StepsGroup],
    actual_steps: Sequence[Step],
    matches: Sequence[Match]
) -> float:
    scores_by_group = defaultdict(float)
    for ref_group_idx, ref_match_idx, actual_idx, score in matches:
        scores_by_group[ref_group_idx] += score
        reference_steps_groups[ref_group_idx][ref_match_idx]["matches"] \
            = actual_steps[actual_idx]["id"]

    steps_score = 0
    for group_idx in range(len(reference_steps_groups)):
        steps_score += scores_by_group[group_idx] / len(reference_steps_groups[group_idx])
    return steps_score / len(reference_steps_groups)


def get_steps_evaluation(reference: dict, actual: dict) -> dict:
    eval_result = {}
    actual_steps = actual.get("actual_steps", [])
    eval_result["actual_steps"] = actual_steps
    for actual_step in actual_steps:
        if actual_step["name"] == "retrieval":
            from .retrieval_answer import get_retrieval_evaluation_dict
            result = get_retrieval_evaluation_dict(
                question_text=reference["question_text"],
                reference_answer=reference.get("reference_answer"),
                actual_answer=actual.get("actual_answer"),
                actual_contexts=json.loads(actual_step["output"])
            )
            actual_step.update(result)
    if "reference_steps" in reference:
        reference_steps = reference["reference_steps"]
        matches = get_steps_matches(reference_steps, actual_steps)
        eval_result["steps_score"] \
            = evaluate_steps(reference_steps, actual_steps, matches)
        for ref_group_idx, ref_match_idx, act_idx, _ in matches:
            reference_step = reference_steps[ref_group_idx][ref_match_idx]
            actual_step = actual_steps[act_idx]
            if reference_step["name"] == "retrieval":
                from .retrieval_context_texts import \
                    get_retrieval_evaluation_dict
                res = get_retrieval_evaluation_dict(
                    reference_contexts=json.loads(reference_step["output"]),
                    actual_contexts=json.loads(actual_step["output"])
                )
                actual_step.update(res)
    return eval_result
