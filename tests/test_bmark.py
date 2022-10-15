from bmark import Bmark


def func():
    pass


def func2():
    pass


def test_defaults():
    assert Bmark.get_measured_time() is None
    assert Bmark.get_acc_time() == 0
    assert len(Bmark.get_all_acc_times()) == 0


def test_measure_time():
    Bmark.measure_time(func)()
    assert Bmark.get_measured_time() is not None
    assert Bmark.get_acc_time() == 0
    assert len(Bmark.get_all_acc_times()) == 0


def test_acc_total():
    Bmark.accumulate_to_total_time(func)()
    assert Bmark.get_measured_time() is None
    assert Bmark.get_acc_time() != 0
    assert len(Bmark.get_all_acc_times()) == 0


def test_acc_total_two_funcs():
    Bmark.accumulate_to_total_time(func)()
    temp = Bmark.get_acc_time()
    Bmark.accumulate_to_total_time(func2)()
    assert Bmark.get_acc_time() != temp
