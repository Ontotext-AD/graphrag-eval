import re
from datetime import datetime, timedelta, timezone
from typing import Any

from dateutil import parser


def normalize_str_value(val: str | list[str] | None) -> list[str] | None:
    if not val:
        return val
    if type(val) == str:
        return [val]
    return sorted(val)


def normalize_granularity(granularity: str | None) -> str | None:
    if not granularity:
        return granularity

    match = re.match(r"(\d+)([a-zA-Z]+)", granularity)

    if not match:
        return granularity

    value, unit = match.groups()

    unit_mapping = {
        "s": "seconds",
        "second": "seconds",
        "m": "minutes",
        "minute": "minutes",
        "h": "hours",
        "hour": "hours",
        "d": "days",
        "day": "days",
        "w": "weeks",
        "week": "weeks",
        "mo": "months",
        "month": "months",
        "q": "quarters",
        "quarter": "quarters",
        "y": "years",
        "year": "years",
    }
    unit = unit_mapping.get(unit.lower(), unit.lower())

    return f"{value}{unit}"


def normalize_relative_time(time_str: str) -> str:
    time_str = re.sub(r"(\d+)m-(ago|ahead)", lambda m: f"{int(m.group(1)) * 60}s-{m.group(2)}", time_str)
    time_str = re.sub(r"(\d+)h-(ago|ahead)", lambda m: f"{int(m.group(1)) * 60 * 60}s-{m.group(2)}", time_str)
    time_str = re.sub(r"(\d+)d-(ago|ahead)", lambda m: f"{int(m.group(1)) * 24 * 60 * 60}s-{m.group(2)}", time_str)
    time_str = re.sub(r"(\d+)w-(ago|ahead)", lambda m: f"{int(m.group(1)) * 7 * 24 * 60 * 60}s-{m.group(2)}", time_str)
    return time_str


def is_relative_time(time_str: str) -> bool:
    return bool(re.match(r"^((\d+([smhdw])-(ago|ahead))|now)$", time_str))


def relative_to_absolute_point_in_time(relative_time: str, anchor_time: datetime) -> datetime:
    if relative_time == "now":
        return anchor_time

    normalized = normalize_relative_time(relative_time)
    m = re.match(r"^(\d+)s-(ago|ahead)$", normalized)

    seconds = int(m.group(1))
    direction = m.group(2)
    delta = timedelta(seconds=seconds)
    return anchor_time - delta if direction == "ago" else anchor_time + delta


def normalize_point_in_time(p: str | datetime, anchor_time: datetime) -> str | datetime:
    if isinstance(p, str):
        if is_relative_time(p):
            return relative_to_absolute_point_in_time(p, anchor_time)
        else:
            try:
                return parser.isoparse(p)
            except ValueError:
                pass
    return p


def to_utc_timezone(datetime_string: str | datetime) -> str | datetime:
    if isinstance(datetime_string, str):
        return datetime_string
    if datetime_string.tzinfo is None:
        datetime_string = datetime_string.replace(tzinfo=timezone.utc)
    return datetime_string.astimezone(timezone.utc)


def compare_points_in_time(
    anchor_time: datetime,
    reference_time: str | datetime | None,
    actual_time: str | datetime | None,
    tolerance_seconds: int = 60,
) -> bool:
    if reference_time is None and actual_time is None:
        return True
    if reference_time is None or actual_time is None:
        return False

    reference_is_rel = isinstance(reference_time, str) and is_relative_time(reference_time)
    actual_is_rel = isinstance(actual_time, str) and is_relative_time(actual_time)

    # If reference is absolute, actual must not be relative
    if not reference_is_rel and actual_is_rel:
        return False

    # Tolerance only when reference is relative and actual is absolute
    use_tolerance = reference_is_rel and not actual_is_rel

    anchor_utc = to_utc_timezone(anchor_time)

    v_ref = to_utc_timezone(normalize_point_in_time(reference_time, anchor_utc))
    v_act = to_utc_timezone(normalize_point_in_time(actual_time, anchor_utc))

    if isinstance(v_ref, datetime) and isinstance(v_act, datetime):
        if use_tolerance:
            diff = abs((v_ref - v_act).total_seconds())
            return diff <= tolerance_seconds
        return v_ref == v_act

    return v_ref == v_act


def compare_retrieve_time_series(reference_step: dict[str, Any], actual_step: dict[str, Any]) -> float:
    reference_args = reference_step["args"]
    actual_args = actual_step["args"]
    if "mrid" in reference_args:
        if "limit" in reference_args:
            return float(
                normalize_str_value(reference_args["mrid"]) == normalize_str_value(actual_args.get("mrid")) \
                and reference_args["limit"] == actual_args.get("limit")
            )
        else:
            return float(
                normalize_str_value(reference_args["mrid"]) == normalize_str_value(actual_args.get("mrid"))
            )
    else:
        return float(
            "mrid" not in actual_args and reference_args.get("limit") == actual_args.get("limit")
        )


def compare_retrieve_data_points(
    reference_step: dict[str, Any],
    actual_step: dict[str, Any],
    anchor_time: datetime,
) -> float:
    reference_args = reference_step["args"]
    actual_args = actual_step["args"]
    return float(
        normalize_str_value(reference_args["external_id"]) == normalize_str_value(actual_args["external_id"]) \
        and normalize_granularity(reference_args.get("granularity")) == normalize_granularity(
            actual_args.get("granularity")) \
        and normalize_str_value(reference_args.get("aggregates")) == normalize_str_value(
            actual_args.get("aggregates")) \
        and compare_points_in_time(anchor_time, reference_args.get("start"), actual_args.get("start")) \
        and compare_points_in_time(anchor_time, reference_args.get("end"), actual_args.get("end")) \
        and reference_args.get("limit") == actual_args.get("limit")
    )
