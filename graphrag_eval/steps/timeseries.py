import re
from datetime import datetime, timedelta, timezone
from typing import Any

from dateutil import parser

GRANULARITY_PATTERN = re.compile(r"(\d+)([a-zA-Z]+)")
RELATIVE_TIME_PATTERN = re.compile(r"^((\d+([smhdw])-(ago|ahead))|now)$")
SECONDS_AGO_OR_AHEAD_PATTERN = re.compile(r"^(\d+)s-(ago|ahead)$")
MINUTES_AGO_OR_AHEAD_PATTERN = re.compile(r"(\d+)m-(ago|ahead)")
HOURS_AGO_OR_AHEAD_PATTERN = re.compile(r"(\d+)h-(ago|ahead)")
DAYS_AGO_OR_AHEAD_PATTERN = re.compile(r"(\d+)d-(ago|ahead)")
WEEKS_AGO_OR_AHEAD_PATTERN = re.compile(r"(\d+)w-(ago|ahead)")


def normalize_str_values(vals: str | list[str] | None) -> list[str] | None:
    if not vals:
        return vals
    if isinstance(vals, str):
        return [vals]
    return sorted(vals)


def normalize_granularity(granularity: str | None) -> str | None:
    if not granularity:
        return granularity

    match = GRANULARITY_PATTERN.match(granularity)

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


def normalize_relative_time(time: str) -> str:
    time = re.sub(MINUTES_AGO_OR_AHEAD_PATTERN, lambda m: f"{int(m.group(1)) * 60}s-{m.group(2)}", time)
    time = re.sub(HOURS_AGO_OR_AHEAD_PATTERN, lambda m: f"{int(m.group(1)) * 60 * 60}s-{m.group(2)}", time)
    time = re.sub(DAYS_AGO_OR_AHEAD_PATTERN, lambda m: f"{int(m.group(1)) * 24 * 60 * 60}s-{m.group(2)}", time)
    time = re.sub(WEEKS_AGO_OR_AHEAD_PATTERN, lambda m: f"{int(m.group(1)) * 7 * 24 * 60 * 60}s-{m.group(2)}", time)
    return time


def is_relative_time(time: str) -> bool:
    return bool(RELATIVE_TIME_PATTERN.match(time))


def relative_to_absolute_time(relative_time: str, anchor_time: datetime) -> datetime:
    if relative_time == "now":
        return anchor_time

    normalized = normalize_relative_time(relative_time)
    m = re.match(SECONDS_AGO_OR_AHEAD_PATTERN, normalized)
    seconds, direction = int(m.group(1)), m.group(2)

    sign = 2 * int(direction == "ahead") - 1
    delta = timedelta(seconds=seconds)
    return anchor_time + sign * delta


def normalize_time(time: str | datetime, anchor_time: datetime) -> str | datetime:
    if isinstance(time, str):
        if is_relative_time(time):
            return relative_to_absolute_time(time, anchor_time)
        else:
            try:
                return parser.isoparse(time)
            except ValueError:
                pass
    return time


def to_utc_timezone(date_time: str | datetime) -> str | datetime:
    if isinstance(date_time, str):
        return date_time
    if date_time.tzinfo is None:
        date_time = date_time.replace(tzinfo=timezone.utc)
    return date_time.astimezone(timezone.utc)


def do_times_equal(
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

    anchor_utc = to_utc_timezone(anchor_time)
    ref_utc = to_utc_timezone(normalize_time(reference_time, anchor_utc))
    act_utc = to_utc_timezone(normalize_time(actual_time, anchor_utc))

    if isinstance(ref_utc, datetime) and isinstance(act_utc, datetime):
        # Tolerance applies only when the reference time is relative and the actual is absolute
        if reference_is_rel and not actual_is_rel:
            diff = abs((ref_utc - act_utc).total_seconds())
            return diff <= tolerance_seconds
        return ref_utc == act_utc

    return ref_utc == act_utc


def do_retrieve_time_series_steps_equal(
    reference_step: dict[str, Any],
    actual_step: dict[str, Any]
) -> bool:
    reference_args = reference_step["args"]
    actual_args = actual_step["args"]

    ref_mrid, ref_limit = reference_args.get("mrid"), reference_args.get("limit")
    act_mrid, act_limit = actual_args.get("mrid"), actual_args.get("limit")

    if ref_mrid:
        norm_ref_mrid = normalize_str_values(ref_mrid)
        norm_act_mrid = normalize_str_values(act_mrid)

        if ref_limit:
            return norm_ref_mrid == norm_act_mrid and ref_limit == act_limit
        else:
            return norm_ref_mrid == norm_act_mrid
    else:
        return act_mrid is None and ref_limit == act_limit


def do_retrieve_data_points_steps_equal(
    reference_step: dict[str, Any],
    actual_step: dict[str, Any],
    anchor_time: datetime,
) -> bool:
    reference_args = reference_step["args"]
    actual_args = actual_step["args"]

    norm_ref_external_id = normalize_str_values(reference_args["external_id"])
    norm_ref_granularity = normalize_granularity(reference_args.get("granularity"))
    norm_ref_aggregates = normalize_str_values(reference_args.get("aggregates"))
    ref_start_time, ref_end_time = reference_args.get("start"), reference_args.get("end")
    ref_limit = reference_args.get("limit")

    norm_act_external_id = normalize_str_values(actual_args["external_id"])
    norm_act_granularity = normalize_granularity(actual_args.get("granularity"))
    norm_act_aggregates = normalize_str_values(actual_args.get("aggregates"))
    act_start_time, act_end_time = actual_args.get("start"), actual_args.get("end")
    act_limit = actual_args.get("limit")

    return norm_ref_external_id == norm_act_external_id \
        and norm_ref_granularity == norm_act_granularity \
        and norm_ref_aggregates == norm_act_aggregates \
        and do_times_equal(anchor_time, ref_start_time, act_start_time) \
        and do_times_equal(anchor_time, ref_end_time, act_end_time) \
        and ref_limit == act_limit
