from bmark import Bmark


@Bmark.measure_time("func")
def func():
    pass


@Bmark.measure_time("func2")
def func2():
    pass


class Cls:
    def __init__(self):
        pass

    @Bmark.measure_time("class")
    def method(self):
        pass


def test_defaults():
    assert Bmark.get_measured_time() is None
    assert Bmark.get_func_times("func") is None


def test_measure_time():
    func()
    assert Bmark.get_measured_time() is not None
    assert Bmark.get_func_times("func") is None


def test_measure_time_accumulate():
    Bmark.enable_accumulating()
    func()
    assert Bmark.get_measured_time() is not None
    assert Bmark.get_func_times("func") is not None
    assert len(Bmark.get_func_times("func")) == 1  # type: ignore
    assert Bmark.get_func_times("func2") is None


def test_measure_time_acc_two_funcs():
    Bmark.enable_accumulating()
    func()
    func2()
    assert Bmark.get_measured_time() is not None
    assert Bmark.get_func_times("func") is not None
    assert Bmark.get_func_times("func2") is not None
    assert len(Bmark.get_func_times("func")) == 1  # type: ignore
    assert len(Bmark.get_func_times("func2")) == 1  # type: ignore


def test_measure_time_acc_two_funcs_sum():
    Bmark.enable_accumulating()
    func()
    func2()
    time1 = Bmark.get_time_sum_func("func")
    time2 = Bmark.get_time_sum_func("func2")
    time_sum = Bmark.get_time_sum_all_funcs()
    assert time_sum == (time1 + time2)  # type: ignore


def test_time_reset():
    func()
    Bmark.reset_measured_time()
    assert Bmark.get_measured_time() is None


def test_deleting_func_times():
    Bmark.enable_accumulating()
    func()
    func2()
    Bmark.delete_func_times("func")
    assert Bmark.get_func_times("func") is None
    assert Bmark.get_func_times("func2") is not None
    assert Bmark.get_time_sum_func("func") is None
    assert Bmark.get_time_sum_all_funcs() is not None


def test_deleting_all_func_times():
    Bmark.enable_accumulating()
    func()
    func2()
    Bmark.delete_all_func_times()
    assert Bmark.get_func_times("func") is None
    assert Bmark.get_func_times("func2") is None
    assert Bmark.get_time_sum_func("func") is None
    assert Bmark.get_time_sum_func("func2") is None
    assert Bmark.get_time_sum_all_funcs() is None


def test_class():
    Bmark.enable_accumulating()
    cls = Cls()
    cls.method()
    assert Bmark.get_func_times("class") is not None
    assert Bmark.get_time_sum_func("class") is not None
    assert Bmark.get_time_sum_all_funcs() is not None
