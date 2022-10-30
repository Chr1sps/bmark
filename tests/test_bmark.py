import pytest
from bmark import Bmark


@Bmark.measure_time()
def func():
    pass


@Bmark.measure_time("func1")
def func1():
    pass


@Bmark.measure_time("func2")
def func2():
    pass


@Bmark.measure_time("func1", "func2")
def func12():
    pass


@pytest.fixture(autouse=True)
def reset_bmark():
    Bmark.reset_to_default()


class Cls:
    def __init__(self):
        pass

    @Bmark.measure_time("class")
    def method(self):
        pass


def test_defaults():
    assert Bmark.get_measured_time() is None
    assert Bmark.get_times_funcs("func1") is None


def test_measure_time():
    func1()
    assert Bmark.get_measured_time() is not None
    assert Bmark.get_times_funcs("func1") is None


def test_measure_time_accumulate():
    Bmark.enable_accumulating()
    func1()
    assert Bmark.get_measured_time() is not None
    assert Bmark.get_times_funcs("func1") is not None
    assert len(Bmark.get_times_funcs("func1")) == 1  # type: ignore
    assert Bmark.get_times_funcs("func2") is None


def test_measure_time_acc_two_funcs():
    Bmark.enable_accumulating()
    func1()
    func2()
    assert Bmark.get_measured_time() is not None
    assert Bmark.get_times_funcs("func1") is not None
    assert Bmark.get_times_funcs("func2") is not None
    assert len(Bmark.get_times_funcs("func1")) == 1  # type: ignore
    assert len(Bmark.get_times_funcs("func2")) == 1  # type: ignore


def test_measure_time_acc_two_funcs_sum():
    Bmark.enable_accumulating()
    func1()
    func2()
    time1 = Bmark.get_time_sum_funcs("func1")
    time2 = Bmark.get_time_sum_funcs("func2")
    time_sum = Bmark.get_time_sum_all_funcs()
    assert time_sum == (time1 + time2)  # type: ignore


def test_measure_time_acc_no_id():
    Bmark.enable_accumulating()
    func()
    assert Bmark.get_time_sum_all_funcs() is None


def test_time_reset():
    func1()
    Bmark.reset_measured_time()
    assert Bmark.get_measured_time() is None


def test_deleting_func_times():
    Bmark.enable_accumulating()
    func1()
    func2()
    Bmark.reset_func_times("func1")
    assert Bmark.get_times_funcs("func1") is None
    assert Bmark.get_times_funcs("func2") is not None
    assert Bmark.get_time_sum_funcs("func1") is None
    assert Bmark.get_time_sum_all_funcs() is not None


def test_deleting_all_func_times():
    Bmark.enable_accumulating()
    func1()
    func2()
    Bmark.reset_all_func_times()
    assert Bmark.get_times_funcs("func1") is None
    assert Bmark.get_times_funcs("func2") is None
    assert Bmark.get_time_sum_funcs("func1") is None
    assert Bmark.get_time_sum_funcs("func2") is None
    assert Bmark.get_time_sum_all_funcs() is None


def test_method():
    Bmark.enable_accumulating()
    cls = Cls()
    cls.method()
    assert Bmark.get_times_funcs("class") is not None
    assert Bmark.get_time_sum_funcs("class") is not None
    assert Bmark.get_time_sum_all_funcs() is not None


def test_measure_time_acc_two_ids():
    Bmark.enable_accumulating()
    func12()
    assert Bmark.get_times_funcs("func1") is not None
    assert Bmark.get_times_funcs("func2") is not None
    assert Bmark.get_time_sum_funcs("func1") is not None
    assert Bmark.get_time_sum_funcs("func2") is not None
    assert Bmark.get_time_sum_all_funcs() is not None


def test_get_multiple_times():
    Bmark.enable_accumulating()
    func1()
    func2()
    dict = Bmark.get_times_funcs("func1", "func2")
    assert "func1" in dict.keys()  # type: ignore
    assert "func2" in dict.keys()  # type: ignore


def test_get_time_sum_funcs_variadic():
    Bmark.enable_accumulating()
    func1()
    func2()
    time1, time2, time12 = (
        Bmark.get_time_sum_funcs("func1"),
        Bmark.get_time_sum_funcs("func2"),
        Bmark.get_time_sum_funcs("func1", "func2"),
    )
    assert time12 == (time1 + time2)  # type: ignore


def test_get_time_sum_funcs_variadic_repeats():
    Bmark.enable_accumulating()
    func1()
    func2()
    time1 = Bmark.get_time_sum_funcs("func1")
    time11 = Bmark.get_time_sum_funcs("func1", "func1")
    assert time1 == time11
