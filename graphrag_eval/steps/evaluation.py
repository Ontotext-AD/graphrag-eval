import json
from collections import defaultdict
from collections.abc import Sequence
from typing import Any

from .iri_discovery import do_iri_discovery_steps_equal
from .retrieval_context_ids import recall_at_k
from .sparql import compare_sparql_results
from .timeseries import do_retrieve_time_series_steps_equal, do_retrieve_data_points_steps_equal

Match = tuple[int, int, int, float]
Step = dict[str, Any]
StepsGroup = Sequence[Step]  # We will index into a group


def compare_steps(reference_step: Step, actual_step: Step) -> float:
    reference_step_name = reference_step["name"]
    actual_step_name = actual_step["name"]
    reference_output = reference_step.get("output")
    actual_output = actual_step["output"]
    reference_output_media_type = reference_step.get("output_media_type")

    if reference_step_name == actual_step_name == "sparql_query" \
        and reference_output_media_type == "application/sparql-results+json":
        return compare_sparql_results(
            json.loads(reference_output),
            json.loads(actual_output),
            reference_step["required_columns"],
            reference_step.get("ordered", False),
            reference_step.get("ignore_duplicates", True),
        )
    elif reference_step_name == actual_step_name == "retrieval" and reference_output:
        ref_contexts_ids = [c["id"] for c in json.loads(reference_output)]
        act_contexts_ids = [c["id"] for c in json.loads(actual_output)]
        k = actual_step["args"]["k"]
        return recall_at_k(ref_contexts_ids, act_contexts_ids, k)
    elif reference_step_name == actual_step_name == "retrieve_time_series":
        return float(do_retrieve_time_series_steps_equal(reference_step, actual_step))
    elif reference_step_name == actual_step_name == "retrieve_data_points":
        return float(
            do_retrieve_data_points_steps_equal(reference_step, actual_step, actual_step["execution_timestamp"])
        )
    elif reference_step_name == "iri_discovery":
        return float(do_iri_discovery_steps_equal(reference_step, actual_step))
    elif reference_step_name == actual_step_name and reference_output_media_type == "application/json":
        return float(json.loads(reference_output) == json.loads(actual_output))
    return float(reference_output == actual_output)


def match_group(
    reference_groups: Sequence[StepsGroup],
    group_idx: int,
    actual_steps: Sequence[Step],
    search_upto: int,
) -> list[Match]:
    used_actual_indices = set()
    matches = []

    reference_group = reference_groups[group_idx]
    for reference_idx, reference_step in reversed(list(enumerate(reference_group))):
        for actual_idx, actual_step in reversed(list(enumerate(actual_steps[:search_upto]))):
            if actual_idx in used_actual_indices or actual_step["status"] != "success":
                continue

            score = compare_steps(reference_step, actual_step)
            if score > 0.0:
                matches.append((group_idx, reference_idx, actual_idx, score))
                used_actual_indices.add(actual_idx)
                break
    return matches


def match_groups(
    reference_groups: Sequence[StepsGroup],
    actual_steps: Sequence[Step],
) -> list[Match]:
    """
    Match the actual steps to the steps in the reference groups such that:
    * Order is preserved (later steps match steps in later reference groups)
    * An actual step can match at most one reference step
    * Extra actual steps are ignored
    * Actual steps with status different from "success" are ignored
    * Matching stops once we find a missing step
    """
    matches = []
    search_upto = len(actual_steps)
    for group_idx, group in reversed(list(enumerate(reference_groups))):
        matched = match_group(reference_groups, group_idx, actual_steps, search_upto)
        if len(matched) == len(group):
            matches.extend(matched)
            search_upto = min(actual_idx for (_, _, actual_idx, _) in matched)
        elif len(matched) < len(group):
            matches.extend(matched)
            break  # a step is not matched and missing, abort
        else:
            break  # a step is not matched and missing, abort
    return matches


def calculate_steps_score(
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


async def evaluate_steps(reference: dict, actual: dict) -> dict:
    eval_result = {}
    actual_steps = actual.get("actual_steps", [])
    eval_result["actual_steps"] = actual_steps
    for actual_step in actual_steps:
        if actual_step["name"] == "retrieval" and "output" in actual_step and "reference_answer" in reference:
            from .retrieval_answer import get_retrieval_evaluation_dict
            result = await get_retrieval_evaluation_dict(
                question_text=reference["question_text"],
                reference_answer=reference["reference_answer"],
                actual_contexts=json.loads(actual_step["output"])
            )
            actual_step.update(result)
    if "reference_steps" in reference:
        reference_steps = reference["reference_steps"]
        matches = match_groups(reference_steps, actual_steps)
        eval_result["steps_score"] = calculate_steps_score(reference_steps, actual_steps, matches)
        for ref_group_idx, ref_match_idx, act_idx, _ in matches:
            reference_step = reference_steps[ref_group_idx][ref_match_idx]
            actual_step = actual_steps[act_idx]
            if reference_step["name"] == "retrieval" and "output" in actual_step:
                from .retrieval_context_texts import get_retrieval_evaluation_dict
                actual_step.update(await get_retrieval_evaluation_dict(
                    reference_answer=reference["reference_answer"],
                    actual_contexts=json.loads(actual_step["output"])
                ))
    return eval_result
