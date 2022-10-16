from bmark import Bmark


def func():
    pass


def func2():
    pass


def test_defaults():
    assert Bmark.get_measured_time() is None
    assert Bmark.get_func_times(func) is None


def test_measure_time():
    Bmark.measure_time(func)()
    assert Bmark.get_measured_time() is not None
    assert Bmark.get_func_times(func) is None


def test_measure_time_accumulate():
    Bmark.enable_accumulating()
    Bmark.measure_time(func)()
    assert Bmark.get_measured_time() is not None
    assert Bmark.get_func_times(func) is not None
    assert len(Bmark.get_func_times(func)) == 1
    assert Bmark.get_func_times(func2) is None


def test_measure_time_acc_two_funcs():
    Bmark.enable_accumulating()
    Bmark.measure_time(func)()
    Bmark.measure_time(func2)()
    assert Bmark.get_measured_time() is not None
    assert Bmark.get_func_times(func) is not None
    assert Bmark.get_func_times(func2) is not None
    assert len(Bmark.get_func_times(func)) == 1
    assert len(Bmark.get_func_times(func2)) == 1
