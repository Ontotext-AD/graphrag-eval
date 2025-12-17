from datetime import datetime

import pytest

from graphrag_eval.steps.timeseries import (
    normalize_str_values,
    normalize_granularity,
    normalize_relative_time,
    is_relative_time,
    compare_points_in_time,
    compare_retrieve_time_series,
    compare_retrieve_data_points,
)


def test_normalize_str_values():
    assert normalize_str_values(None) is None
    assert normalize_str_values("string") == ["string"]
    assert normalize_str_values(["string"]) == ["string"]
    assert normalize_str_values(["s2", "s1"]) == ["s1", "s2"]


def test_normalize_granularity():
    assert normalize_granularity(None) is None
    assert normalize_granularity("month1") == "month1"
    assert normalize_granularity("1decade") == "1decade"
    assert normalize_granularity("1s") == "1seconds"
    assert normalize_granularity("1second") == "1seconds"
    assert normalize_granularity("5SECONDS") == "5seconds"
    assert normalize_granularity("1m") == "1minutes"
    assert normalize_granularity("1minute") == "1minutes"
    assert normalize_granularity("5MINUTES") == "5minutes"
    assert normalize_granularity("1h") == "1hours"
    assert normalize_granularity("1hour") == "1hours"
    assert normalize_granularity("5HOURS") == "5hours"
    assert normalize_granularity("1d") == "1days"
    assert normalize_granularity("1day") == "1days"
    assert normalize_granularity("5DAYS") == "5days"
    assert normalize_granularity("1w") == "1weeks"
    assert normalize_granularity("1week") == "1weeks"
    assert normalize_granularity("5WEEKS") == "5weeks"
    assert normalize_granularity("1mo") == "1months"
    assert normalize_granularity("1month") == "1months"
    assert normalize_granularity("5MONTHS") == "5months"
    assert normalize_granularity("1q") == "1quarters"
    assert normalize_granularity("1quarter") == "1quarters"
    assert normalize_granularity("2QUARTERS") == "2quarters"
    assert normalize_granularity("1y") == "1years"
    assert normalize_granularity("1year") == "1years"
    assert normalize_granularity("2YEARS") == "2years"


def test_normalize_relative_time():
    assert normalize_relative_time("1024s-ago") == "1024s-ago"
    assert normalize_relative_time("1024s-ahead") == "1024s-ahead"
    assert normalize_relative_time("100m-ago") == "6000s-ago"
    assert normalize_relative_time("100m-ahead") == "6000s-ahead"
    assert normalize_relative_time("3h-ago") == "10800s-ago"
    assert normalize_relative_time("3h-ahead") == "10800s-ahead"
    assert normalize_relative_time("5d-ago") == "432000s-ago"
    assert normalize_relative_time("5d-ahead") == "432000s-ahead"
    assert normalize_relative_time("1w-ago") == "604800s-ago"
    assert normalize_relative_time("1w-ahead") == "604800s-ahead"


def test_is_relative_time():
    assert is_relative_time("1024s-ago") == True
    assert is_relative_time("1024s-ahead") == True
    assert is_relative_time("1024seconds-ago") == False
    assert is_relative_time("1024seconds-ahead") == False
    assert is_relative_time("-1024seconds-ago") == False
    assert is_relative_time("-1024seconds-ahead") == False
    assert is_relative_time("1second-ago") == False
    assert is_relative_time("1second-ahead") == False

    assert is_relative_time("100m-ago") == True
    assert is_relative_time("100m-ahead") == True
    assert is_relative_time("100minutes-ago") == False
    assert is_relative_time("100minutes-ahead") == False
    assert is_relative_time("-100minutes-ago") == False
    assert is_relative_time("-100minutes-ahead") == False
    assert is_relative_time("1minute-ago") == False
    assert is_relative_time("1minute-ahead") == False

    assert is_relative_time("3h-ago") == True
    assert is_relative_time("3h-ahead") == True
    assert is_relative_time("3hours-ago") == False
    assert is_relative_time("3hours-ahead") == False
    assert is_relative_time("-3hours-ago") == False
    assert is_relative_time("-3hours-ahead") == False
    assert is_relative_time("1hour-ago") == False
    assert is_relative_time("1hour-ahead") == False

    assert is_relative_time("5d-ago") == True
    assert is_relative_time("5d-ahead") == True
    assert is_relative_time("5days-ago") == False
    assert is_relative_time("5days-ahead") == False
    assert is_relative_time("-5days-ago") == False
    assert is_relative_time("-5days-ahead") == False
    assert is_relative_time("1day-ago") == False
    assert is_relative_time("1day-ahead") == False

    assert is_relative_time("1w-ago") == True
    assert is_relative_time("1w-ahead") == True
    assert is_relative_time("5weeks-ago") == False
    assert is_relative_time("5weeks-ahead") == False
    assert is_relative_time("-5weeks-ago") == False
    assert is_relative_time("-5weeks-ahead") == False
    assert is_relative_time("1week-ago") == False
    assert is_relative_time("1week-ahead") == False

    assert is_relative_time("1mo-ago") == False
    assert is_relative_time("1mo-ahead") == False
    assert is_relative_time("5months-ago") == False
    assert is_relative_time("5months-ahead") == False
    assert is_relative_time("-5months-ago") == False
    assert is_relative_time("-5months-ahead") == False
    assert is_relative_time("1month-ago") == False
    assert is_relative_time("1month-ahead") == False

    assert is_relative_time("1q-ago") == False
    assert is_relative_time("1q-ahead") == False
    assert is_relative_time("2quarters-ago") == False
    assert is_relative_time("2quarters-ahead") == False
    assert is_relative_time("-2quarters-ago") == False
    assert is_relative_time("-2quarters-ahead") == False
    assert is_relative_time("1quarter-ago") == False
    assert is_relative_time("1quarter-ahead") == False

    assert is_relative_time("1y-ago") == False
    assert is_relative_time("1y-ahead") == False
    assert is_relative_time("5years-ago") == False
    assert is_relative_time("5years-ahead") == False
    assert is_relative_time("-5years-ago") == False
    assert is_relative_time("-5years-ahead") == False
    assert is_relative_time("1year-ago") == False
    assert is_relative_time("1year-ahead") == False

    assert is_relative_time("now") == True
    assert is_relative_time("yesterday") == False
    assert is_relative_time("tomorrow") == False


def test_relative_to_absolute_point_in_time():
    assert True


@pytest.mark.parametrize(
    "anchor_time, p1, p2, match",
    [
        # absolute vs. absolute (NO tolerance)
        (datetime.fromisoformat("2025-01-01T00:10:00Z"), "2025-01-01T00:00:00Z", "2025-01-01T00:00:00Z", True),
        # diff 30s but still False
        (datetime.fromisoformat("2025-01-01T00:10:00Z"), "2025-01-01T00:00:30Z", "2025-01-01T00:00:00Z", False),
        (datetime.now(), "2025-01-01T00:00:00Z", "2025-01-01T00:00:00Z", True),
        (datetime.now(), "2025-01-01T00:00:00Z", "2025-01-01T00:00:00", True),
        (datetime.now(), "2025-01-01T00:00:00Z", "2025-01-01T02:00:00+02:00", True),
        (datetime.now(), "2025-01-01T01", "2025-01-01T01", True),
        (datetime.now(), "2025-01-01T01:30", "2025-01-01T01:30", True),
        (datetime.now(), "2025-01-01T01:30:30", "2025-01-01T01:30:30", True),
        (datetime.now(), "2025-01-01T01:30:30.123", "2025-01-01T01:30:30.123", True),
        (datetime.now(), "2025-01-01T01:30:30.123Z", "2025-01-01T01:30:30.123Z", True),
        (datetime.now(), "2025-01-01T01:30:30.123Z", "2025-01-01T01:30:30.123", True),
        (datetime.now(), "2025-01-01T01:30:30.123Z", "2025-01-01T03:30:30.123+02:00", True),
        (datetime.now(), "2025-13-01", "2025-13-01", True),
        (datetime.now(), "2025-01-01T00:00:00Z", "2024-12-31T23:59:59Z", False),
        # mixed: relative vs. absolute (tolerance applies)
        # relative vs. relative
        (datetime.fromisoformat("2025-01-01T00:00:00Z"), "now", "now", True),
        (datetime.now(), "2h-ago", "2h-ago", True),
        (datetime.now(), "1w-ago", "7d-ago", True),
        (datetime.now(), "1d-ago", "24h-ago", True),
        (datetime.now(), "1h-ahead", "60m-ahead", True),
        (datetime.now(), "1m-ago", "60s-ago", True),
        # different instants, no tolerance
        (datetime.fromisoformat("2025-01-01T00:00:00Z"), "1m-ago", "30s-ago", False),
        # None handling
        (datetime.now(), None, None, True),
        (datetime.now(), "now", None, False),
        (datetime.now(), "2025-01-01T00:00:00Z", None, False),
        # unparseable strings fall back to strict equality
        (datetime.fromisoformat("2025-01-01T00:00:00Z"), "yesterday", "yesterday", True),
        (datetime.fromisoformat("2025-01-01T00:00:00Z"), "yesterday", "today", False),
    ],
)
def test_compare_datetime(anchor_time: datetime, p1, p2, match: bool):
    assert compare_points_in_time(anchor_time, p1, p2) == match
    assert compare_points_in_time(anchor_time, p2, p1) == match


@pytest.mark.parametrize(
    "anchor_time, reference_time, actual_time, match",
    [
        # mixed: relative vs. absolute (tolerance applies)
        (datetime.fromisoformat("2025-01-01T00:00:00Z"), "now", "2025-01-01T00:00:00Z", True),
        (datetime.fromisoformat("2025-01-01T00:00:00Z"), "2025-01-01T00:00:00Z", "now", False),
        (datetime.fromisoformat("2025-01-01T00:00:30Z"), "now", "2025-01-01T00:00:00Z", True),
        (datetime.fromisoformat("2025-01-01T02:00:30+02:00"), "now", "2025-01-01T00:00:00Z", True),
        (datetime.fromisoformat("2025-01-01T00:00:30"), "now", "2025-01-01T00:00:00Z", True),
        (datetime.fromisoformat("2025-01-01T00:01:00Z"), "60s-ago", "2025-01-01T00:00:00Z", True),
        (datetime.fromisoformat("2025-01-01T00:01:01Z"), "60s-ago", "2025-01-01T00:00:00Z", True),
        (datetime.fromisoformat("2025-01-01T00:01:01Z"), "1m-ago", "2025-01-01T00:00:00Z", True),
        (datetime.fromisoformat("2025-01-01T00:03:30Z"), "2m-ago", "2025-01-01T00:00:00Z", False),
        (datetime.fromisoformat("2025-01-01T02:00:00Z"), "2h-ago", "2025-01-01T00:00:00Z", True),
    ],
)
def test_compare_datetime_relative_vs_absolute(anchor_time: datetime, reference_time, actual_time, match: bool):
    assert compare_points_in_time(anchor_time, reference_time, actual_time) == match


def test_compare_retrieve_time_series():
    reference_step = {
        "name": "retrieve_time_series",
        "args": {
        }
    }
    actual_step = {
        "name": "retrieve_time_series",
        "args": {
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_time_series(reference_step, actual_step) == True

    reference_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": "9bb00fb1-4e7f-831a-e040-1e828c94e833",
        }
    }
    actual_step = {
        "name": "retrieve_time_series",
        "args": {
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_time_series(reference_step, actual_step) == False

    reference_step = {
        "name": "retrieve_time_series",
        "args": {
        }
    }
    actual_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": "9bb00fb1-4e7f-831a-e040-1e828c94e833",
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_time_series(reference_step, actual_step) == False

    reference_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": "9bb00fb1-4e7f-831a-e040-1e828c94e833",
        }
    }
    actual_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": "9bb00fb1-4e7f-831a-e040-1e828c94e833",
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_time_series(reference_step, actual_step) == True

    reference_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": "9bb00fb1-4e7f-831a-e040-1e828c94e833",
        }
    }
    actual_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": "9bb00fb1-4e7f-831a-e040-1e828c94e833",
            "limit": 5,
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_time_series(reference_step, actual_step) == True

    reference_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": "9bb00fb1-4e7f-831a-e040-1e828c94e833",
        }
    }
    actual_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": ["9bb00fb1-4e7f-831a-e040-1e828c94e833"],
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_time_series(reference_step, actual_step) == True

    reference_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": [
                "9bb00fb1-4e7f-831a-e040-1e828c94e833",
                "62cef574-c2e3-428e-9cf7-469e572d524e",
            ],
        }
    }
    actual_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": [
                "62cef574-c2e3-428e-9cf7-469e572d524e",
                "9bb00fb1-4e7f-831a-e040-1e828c94e833",
            ],
            "limit": 10,
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_time_series(reference_step, actual_step) == True

    reference_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": ["9bb00fb1-4e7f-831a-e040-1e828c94e833"],
        }
    }
    actual_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": [
                "62cef574-c2e3-428e-9cf7-469e572d524e",
                "9bb00fb1-4e7f-831a-e040-1e828c94e833",
            ],
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_time_series(reference_step, actual_step) == False

    reference_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": ["9bb00fb1-4e7f-831a-e040-1e828c94e833"],
            "limit": 5,
        }
    }
    actual_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": ["9bb00fb1-4e7f-831a-e040-1e828c94e833"],
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_time_series(reference_step, actual_step) == False

    reference_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": ["9bb00fb1-4e7f-831a-e040-1e828c94e833"],
            "limit": 5,
        }
    }
    actual_step = {
        "name": "retrieve_time_series",
        "args": {
            "mrid": ["9bb00fb1-4e7f-831a-e040-1e828c94e833"],
            "limit": 5,
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_time_series(reference_step, actual_step) == True


def test_compare_retrieve_data_points():
    reference_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": "9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value",
        }
    }
    actual_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": "9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value",
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_data_points(reference_step, actual_step, datetime.now()) == True

    reference_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": "9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value",
        }
    }
    actual_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": ["9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value"],
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_data_points(reference_step, actual_step, datetime.now()) == True

    reference_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": [
                "9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value",
                "62cef574-c2e3-428e-9cf7-469e572d524e_estimated_value",
            ],
        }
    }
    actual_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": [
                "62cef574-c2e3-428e-9cf7-469e572d524e_estimated_value",
                "9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value",
            ],
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_data_points(reference_step, actual_step, datetime.now()) == True

    reference_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": "9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value",
        }
    }
    actual_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": "9bb00fb1-4e7f-831a-e040-1e828c94e833",
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_data_points(reference_step, actual_step, datetime.now()) == False

    reference_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": "9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value",
            "limit": 10,
        }
    }
    actual_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": ["9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value"],
            "limit": 10,
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_data_points(reference_step, actual_step, datetime.now()) == True

    reference_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": "9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value",
            "limit": 10,
        }
    }
    actual_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": ["9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value"]
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_data_points(reference_step, actual_step, datetime.now()) == False

    reference_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": "9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value",
            "aggregates": "average",
            "granularity": "1w",
            "start": "2025-01-01T00:00:00Z",
        }
    }
    actual_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": ["9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value"],
            "aggregates": ["average"],
            "granularity": "1week",
            "start": "2025-01-01T00:00:00Z",
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_data_points(reference_step, actual_step, datetime.now()) == True

    reference_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": "9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value",
            "aggregates": ["average", "min", "max"],
            "granularity": "1w",
            "start": "2025-01-01T00:00:00Z",
            "end": "2026-01-01T00:00:00Z",
        }
    }
    actual_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": ["9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value"],
            "aggregates": ["min", "max", "average"],
            "granularity": "1week",
            "start": "2025-01-01T00:00:00Z",
            "end": "2026-01-01T00:00:00Z",
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_data_points(reference_step, actual_step, datetime.now()) == True

    reference_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": "9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value",
            "aggregates": ["average", "min", "max"],
            "granularity": "1w",
            "start": "2025-01-01T00:00:00Z",
            "end": "2026-01-01T00:00:00Z",
        }
    }
    actual_step = {
        "name": "retrieve_data_points",
        "args": {
            "external_id": ["9bb00fb1-4e7f-831a-e040-1e828c94e833_estimated_value"],
            "aggregates": ["min", "max", "average"],
            "granularity": "1week",
            "start": "2025-01-01T00:00:00Z",
            "end": "2025-12-31T23:59:59Z",
        },
        "id": "call_1MA7PL4KAPJ7riH2UrxseyZW",
        "status": "success",
    }
    assert compare_retrieve_data_points(reference_step, actual_step, datetime.now()) == False
