import gc

import pytest

import bmark


@bmark.measure_time()
def func():
    pass


@bmark.measure_time("func1")
def func1():
    pass


@bmark.measure_time("func2")
def func2():
    pass


@bmark.measure_time("func1", "func2")
def func12():
    pass


@pytest.fixture(autouse=True)
def reset_bmark():
    bmark.reset_to_default()


def dummy():
    pass


@bmark.measure_time()
def gc_check():
    return gc.isenabled()


class Cls:
    def __init__(self):
        pass

    @bmark.measure_time("class")
    def method(self):
        pass


def test_defaults():
    assert bmark.get_measured_time() is None
    assert bmark.get_times_funcs("func1") is None


def test_measure_time():
    func1()
    assert bmark.get_measured_time() is not None
    assert bmark.get_times_funcs("func1") is None


def test_measure_time_accumulate():
    bmark.set_accumulating(True)
    func1()
    assert bmark.get_measured_time() is not None
    assert bmark.get_times_funcs("func1") is not None
    assert len(bmark.get_times_funcs("func1")) == 1  # type: ignore
    assert bmark.get_times_funcs("func2") is None


def test_measure_time_acc_two_funcs():
    bmark.set_accumulating(True)
    func1()
    func2()
    assert bmark.get_measured_time() is not None
    assert bmark.get_times_funcs("func1") is not None
    assert bmark.get_times_funcs("func2") is not None
    assert len(bmark.get_times_funcs("func1")) == 1  # type: ignore
    assert len(bmark.get_times_funcs("func2")) == 1  # type: ignore


def test_measure_time_acc_two_funcs_sum():
    bmark.set_accumulating(True)
    func1()
    func2()
    time1 = bmark.get_time_sum_funcs("func1")
    time2 = bmark.get_time_sum_funcs("func2")
    time_sum = bmark.get_time_sum_all_funcs()
    assert time_sum == (time1 + time2)  # type: ignore


def test_measure_time_acc_no_id():
    bmark.set_accumulating(True)
    func()
    assert bmark.get_time_sum_all_funcs() is None


def test_time_reset():
    func1()
    bmark.reset_measured_time()
    assert bmark.get_measured_time() is None


def test_deleting_func_times():
    bmark.set_accumulating(True)
    func1()
    func2()
    bmark.reset_func_times("func1")
    assert bmark.get_times_funcs("func1") is None
    assert bmark.get_times_funcs("func2") is not None
    assert bmark.get_time_sum_funcs("func1") is None
    assert bmark.get_time_sum_all_funcs() is not None


def test_deleting_all_func_times():
    bmark.set_accumulating(True)
    func1()
    func2()
    bmark.reset_all_func_times()
    assert bmark.get_times_funcs("func1") is None
    assert bmark.get_times_funcs("func2") is None
    assert bmark.get_time_sum_funcs("func1") is None
    assert bmark.get_time_sum_funcs("func2") is None
    assert bmark.get_time_sum_all_funcs() is None


def test_method():
    bmark.set_accumulating(True)
    cls = Cls()
    cls.method()
    assert bmark.get_times_funcs("class") is not None
    assert bmark.get_time_sum_funcs("class") is not None
    assert bmark.get_time_sum_all_funcs() is not None


def test_measure_time_acc_two_ids():
    bmark.set_accumulating(True)
    func12()
    assert bmark.get_times_funcs("func1") is not None
    assert bmark.get_times_funcs("func2") is not None
    assert bmark.get_time_sum_funcs("func1") is not None
    assert bmark.get_time_sum_funcs("func2") is not None
    assert bmark.get_time_sum_all_funcs() is not None


def test_get_multiple_times():
    bmark.set_accumulating(True)
    func1()
    func2()
    dict = bmark.get_times_funcs("func1", "func2")
    assert "func1" in dict.keys()  # type: ignore
    assert "func2" in dict.keys()  # type: ignore


def test_get_time_sum_funcs_variadic():
    bmark.set_accumulating(True)
    func1()
    func2()
    time1, time2, time12 = (
        bmark.get_time_sum_funcs("func1"),
        bmark.get_time_sum_funcs("func2"),
        bmark.get_time_sum_funcs("func1", "func2"),
    )
    assert time12 == (time1 + time2)  # type: ignore


def test_get_time_sum_funcs_variadic_repeats():
    bmark.set_accumulating(True)
    func1()
    func2()
    time1 = bmark.get_time_sum_funcs("func1")
    time11 = bmark.get_time_sum_funcs("func1", "func1")
    assert time1 == time11


def test_measure_block():
    with bmark.measure_block("func1"):
        dummy()
    assert bmark.get_measured_time() is not None
    assert bmark.get_times_funcs("func1") is None


def test_not_disabling_gc():
    gc.enable()
    bmark.set_disabled_gc(False)
    result = gc_check()
    assert result


def test_percentile_no_interpolation(monkeypatch):
    test_dict = {"func": [1, 2, 3, 4, 5]}
    monkeypatch.setattr(bmark, "__time_dict", test_dict)
    assert bmark.get_percentile("func", 0) == 1
    assert bmark.get_percentile("func", 25) == 2
    assert bmark.get_percentile("func", 80) == 4


def test_percentile_with_interpolation(monkeypatch):
    test_dict = {"func": [1, 2, 3, 4, 5]}
    monkeypatch.setattr(bmark, "__time_dict", test_dict)
    assert bmark.get_percentile("func", 0, True) == 1
    assert bmark.get_percentile("func", 25, True) == 2
    assert bmark.get_percentile("func", 60, True) == 3.4
    assert bmark.get_percentile("func", 80, True) == 4.2
