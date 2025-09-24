from collections import Counter
import re
from typing import Union
import itertools
import math

XSD_NUMERIC_TYPES = {
    "http://www.w3.org/2001/XMLSchema#integer",
    "http://www.w3.org/2001/XMLSchema#int",
    "http://www.w3.org/2001/XMLSchema#long",
    "http://www.w3.org/2001/XMLSchema#short",
    "http://www.w3.org/2001/XMLSchema#byte",
    "http://www.w3.org/2001/XMLSchema#nonNegativeInteger",
    "http://www.w3.org/2001/XMLSchema#positiveInteger",
    "http://www.w3.org/2001/XMLSchema#unsignedLong",
    "http://www.w3.org/2001/XMLSchema#unsignedInt",
    "http://www.w3.org/2001/XMLSchema#unsignedShort",
    "http://www.w3.org/2001/XMLSchema#unsignedByte",
}
XSD_FLOAT_TYPES = {
    "http://www.w3.org/2001/XMLSchema#decimal",
    "http://www.w3.org/2001/XMLSchema#double",
    "http://www.w3.org/2001/XMLSchema#float",
}
XSD_BOOLEAN = "http://www.w3.org/2001/XMLSchema#boolean"


def truncate(number: float, decimals: int = 0) -> float:
    """
    Truncates a float to a certain number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places must be zero or a positive integer.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0**decimals
    return math.trunc(number * factor) / factor


def parse_sparql_term(term: dict) -> Union[str, float, bool, None]:
    if not isinstance(term, dict):
        return term

    term_type = term.get("type")
    value = term.get("value")

    if term_type in ("literal", "typed-literal"):
        datatype = term.get("datatype")
        if not datatype:
            return value

        if datatype in XSD_NUMERIC_TYPES:
            try:
                return int(value)
            except (ValueError, TypeError):
                return value
        elif datatype in XSD_FLOAT_TYPES:
            try:
                value = float(value)
                return truncate(value, 5)
            except (ValueError, TypeError):
                return value
        elif datatype == XSD_BOOLEAN:
            return value.lower() in ("true", "1")
        else:
            return value

    return value


def get_var_to_values(
    vars_: list[str],
    bindings: list[dict],
) -> dict[str, list]:
    var_to_values = {}
    for var in vars_:
        var_to_values[var] = []
        for binding in bindings:
            if var in binding:
                var_to_values[var].append(parse_sparql_term(binding[var]))
            else:
                var_to_values[var].append(None)
    return dict(var_to_values)


def convert_table_dict2lines(
    reference_vars: Union[list[str], tuple[str, ...]],
    reference_var_to_values: dict[str, list],
) -> list[str]:
    """Converts a dictionary of lists (columns) into a list of row strings.

    This function takes a dictionary where keys are column headers and values are
    lists of column data. It transforms this column-oriented data into a list
    of rows, where each row is a single string formed by concatenating the
    string representation of its cell values.

    It assumes that all lists in the `reference_var_to_values` dictionary
    have the same length.

    Args:
        reference_vars: An ordered list or tuple of keys that defines the
            column order for the output rows.
        reference_var_to_values: A dictionary mapping column names (keys) to
            lists of their corresponding values.

    Returns:
        A list of strings, where each string is a concatenation of the values
        for a single row, ordered according to `reference_vars`.

    Example:
        >>> columns = ['name', 'age', 'city']
        >>> data = {
        ...     'name': ['Alice', 'Bob'],
        ...     'age': [30, 25],
        ...     'city': ['New York', 'Los Angeles']
        ... }
        >>> dict2lines(columns, data)
        ['Alice30New York', 'Bob25Los Angeles']
    """
    result = []
    num_rows = len(reference_var_to_values[reference_vars[0]])
    for row_idx in range(num_rows):
        row = []
        for reference_var in reference_vars:
            val = reference_var_to_values[reference_var][row_idx]
            val = str(val)
            row.append(val)
        result.append("".join(row))
    return result


def compare_values(
    reference_vars: list[str],
    reference_var_to_values: dict[str, list],
    actual_vars: Union[list[str], tuple[str, ...]],
    actual_var_to_values: dict[str, list],
    results_are_ordered: bool,
) -> bool:

    if len(reference_vars) < len(actual_vars):
        for combination in itertools.combinations(actual_vars, len(reference_vars)):
            if compare_values(
                reference_vars,
                reference_var_to_values,
                combination,
                actual_var_to_values,
                results_are_ordered,
            ):
                return True
        return False

    table = convert_table_dict2lines(reference_vars, reference_var_to_values)
    for permutation in itertools.permutations(actual_vars):
        actual_table = convert_table_dict2lines(permutation, actual_var_to_values)
        if (results_are_ordered and table == actual_table) or (
            not results_are_ordered and Counter(table) == Counter(actual_table)
        ):
            return True

    return False


def compare_sparql_results(
    reference_sparql_result: dict,
    actual_sparql_result: dict,
    required_vars: list[str],
    results_are_ordered: bool = False,
) -> float:
    # DESCRIBE results
    if isinstance(actual_sparql_result, str):
        return 0.0

    # ASK
    if "boolean" in reference_sparql_result:
        return float(
            "boolean" in actual_sparql_result
            and reference_sparql_result["boolean"] == actual_sparql_result["boolean"]
        )

    reference_bindings: list[dict] = reference_sparql_result["results"]["bindings"]
    actual_bindings: list[dict] = actual_sparql_result.get("results", dict()).get(
        "bindings", []
    )
    actual_vars: list[str] = actual_sparql_result["head"].get("vars", [])

    if (not actual_bindings) and (not reference_bindings):
        return float(len(actual_vars) >= len(required_vars))
    elif (not actual_bindings) or (not reference_bindings):
        return 0.0
    if len(required_vars) > len(actual_vars):
        return 0.0
    if len(required_vars) == 0:
        return 1.0

    reference_var_to_values: dict[str, list] = get_var_to_values(
        required_vars, reference_bindings
    )
    actual_var_to_values: dict[str, list] = get_var_to_values(
        actual_vars, actual_bindings
    )

    return float(
        compare_values(
            required_vars,
            reference_var_to_values,
            actual_vars,
            actual_var_to_values,
            results_are_ordered,
        )
    )
