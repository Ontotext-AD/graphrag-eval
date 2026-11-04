import pytest
from graphrag_eval.util import compute_f1, get_f1_dict, singleton


def test_compute_f1_normal_values():
    assert compute_f1(1.0, 1.0) == 1.0
    assert pytest.approx(compute_f1(0.5, 0.5)) == 0.5
    assert pytest.approx(compute_f1(0.8, 0.4)) == 2 * (0.8 * 0.4) / (0.8 + 0.4)


def test_compute_f1_string_numbers():
    assert pytest.approx(compute_f1("0.6", "0.6")) == 0.6


def test_compute_f1_zeros():
    assert compute_f1(0.0, 0.0) == 0.0
    assert compute_f1("0", "0") == 0.0


def test_compute_f1_none():
    assert compute_f1(None, 0.5) is None
    assert compute_f1(0.5, None) is None
    assert compute_f1(None, None) is None


def test_get_f1_dict():
    data = {"answer_recall": 0.8, "answer_precision": 0.8}
    result = get_f1_dict(data, "answer")
    assert pytest.approx(result["answer_f1"]) == 0.8

    incomplete_data = {"answer_recall": 0.8}
    assert get_f1_dict(incomplete_data, "answer") == {}


def test_singleton_decorator():
    @singleton
    class DatabaseConnection:
        def __init__(self, name="default"):
            self.name = name

    conn1 = DatabaseConnection("db1")
    conn2 = DatabaseConnection("db2")
    assert conn1 is conn2
    assert conn2.name == "db1"
