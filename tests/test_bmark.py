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
    bmark.restore_defaults()


def dummy():
    pass


@bmark.measure_time()
def gc_check():
    return gc.isenabled()


@pytest.fixture
def mock_time_dict(monkeypatch):
    test_dict = {"func": [7, 5, 6, 6, 1, 2]}
    monkeypatch.setattr(bmark, "_time_dict", test_dict)


class Cls:
    def __init__(self):
        pass

    @bmark.measure_time("class")
    def method(self):
        pass


def test_defaults():
    assert bmark.get_last_time() is None
    assert bmark.get_times("func1") is None


def test_measure_time_no_acc():
    bmark.set_accumulating(False)
    func1()
    assert bmark.get_last_time() is not None
    assert bmark.get_times("func1") is None


def test_measure_time_acc():
    func1()
    assert bmark.get_last_time() is not None
    assert bmark.get_times("func1") is not None
    assert len(bmark.get_times("func1")) == 1  # type: ignore
    assert bmark.get_times("func2") is None


def test_measure_time_acc_two_funcs():
    func1()
    func2()
    assert bmark.get_last_time() is not None
    assert bmark.get_times("func1") is not None
    assert bmark.get_times("func2") is not None
    assert len(bmark.get_times("func1")) == 1  # type: ignore
    assert len(bmark.get_times("func2")) == 1  # type: ignore


def test_measure_time_acc_two_funcs_sum():
    func1()
    func2()
    time1 = bmark.get_time_sum("func1")
    time2 = bmark.get_time_sum("func2")
    time_sum = bmark.get_time_sum()
    assert time_sum == (time1 + time2)  # type: ignore


def test_measure_time_acc_no_id():
    func()
    assert bmark.get_time_sum() is None


def test_time_reset():
    func1()
    bmark.clear_last_time()
    assert bmark.get_last_time() is None


def test_deleting_func_times():
    func1()
    func2()
    bmark.clear_times("func1")
    assert bmark.get_times("func1") is None
    assert bmark.get_times("func2") is not None
    assert bmark.get_time_sum("func1") is None
    assert bmark.get_time_sum() is not None


def test_deleting_all_func_times():
    func1()
    func2()
    bmark.clear_times()
    assert bmark.get_times("func1") is None
    assert bmark.get_times("func2") is None
    assert bmark.get_time_sum("func1") is None
    assert bmark.get_time_sum("func2") is None
    assert bmark.get_time_sum() is None


def test_method():
    cls = Cls()
    cls.method()
    assert bmark.get_times("class") is not None
    assert bmark.get_time_sum("class") is not None
    assert bmark.get_time_sum() is not None


def test_measure_time_acc_two_ids():
    func12()
    assert bmark.get_times("func1") is not None
    assert bmark.get_times("func2") is not None
    assert bmark.get_time_sum("func1") is not None
    assert bmark.get_time_sum("func2") is not None
    assert bmark.get_time_sum() is not None


def test_get_multiple_times():
    func1()
    func2()
    d = bmark.get_times("func1", "func2")
    assert "func1" in d.keys()  # type: ignore
    assert "func2" in d.keys()  # type: ignore


def test_get_time_sum_func_not_found():
    time_sum = bmark.get_time_sum("non-existent", "non-existent2")
    assert time_sum is None


def test_get_time_sum_variadic():
    func1()
    func2()
    time1, time2, time12 = (
        bmark.get_time_sum("func1"),
        bmark.get_time_sum("func2"),
        bmark.get_time_sum("func1", "func2"),
    )
    assert time12 == (time1 + time2)  # type: ignore


def test_get_time_sum_variadic_repeats():
    func1()
    func2()
    time1 = bmark.get_time_sum("func1")
    time11 = bmark.get_time_sum("func1", "func1")
    assert time1 == time11


def test_measure_block():
    with bmark.MeasureBlock("func1"):
        dummy()
    assert bmark.get_last_time() is not None
    assert bmark.get_times("func1") is not None


def test_measure_block_elapsed_and_period():
    with bmark.MeasureBlock("func1") as block:
        dummy()
        measurement = block.elapsed()
        block.period()
        measurement2 = block.period()
    assert bmark.get_last_time() is not None
    assert bmark.get_times("func1") is not None
    assert measurement is not None
    assert measurement2 is not None
    assert measurement > measurement2


def test_measure_block_elapsed_and_period_exception():
    block = bmark.MeasureBlock("func1")
    with pytest.raises(AttributeError):
        block.elapsed()
    with pytest.raises(AttributeError):
        block.period()


def test_not_disabling_gc():
    gc.enable()
    bmark.set_disabled_gc(False)
    result = gc_check()
    assert result


def test_percentile_no_interpolation(mock_time_dict):
    assert bmark.percentile("func", 0) == 1
    assert bmark.percentile("func", 25) == 2
    assert bmark.percentile("func", 80) == 6


def test_percentile_with_interpolation(mock_time_dict):
    assert bmark.percentile("func", 0, True) == 1
    assert bmark.percentile("func", 25, True) == 2.75
    assert bmark.percentile("func", 55, True) == 5.75
    assert bmark.percentile("func", 80, True) == 6


def test_median(mock_time_dict):
    assert bmark.median("func") == 5.5


def test_average(mock_time_dict):
    assert bmark.average("func") == 4.5


def test_std_dev(mock_time_dict):
    assert bmark.std_dev("func") == pytest.approx(2.2173557826)
