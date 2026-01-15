import json
from typing import Any


def do_iri_discovery_steps_equal(
    reference_step: dict[str, Any],
    actual_step: dict[str, Any],
) -> bool:
    if actual_step["name"] != "autocomplete_search":
        return False

    reference_iri = reference_step["output"]
    actual_output = json.loads(actual_step["output"])

    for binding in actual_output["results"]["bindings"]:
        for _, type_value in binding.items():
            if type_value["type"] == "uri" and type_value["value"] == reference_iri:
                return True

    return False
