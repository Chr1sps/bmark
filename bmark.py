import gc
import time
from typing import Callable, Dict


class Bmark:
    """
    A collection of benchmark functions useful in data science applications
    """

    _total_time: float = 0
    _last_time: float | None = None
    _total_time_dict: Dict[Callable, float] = {}

    @staticmethod
    def measure_time(func):
        def wrapper(*args, **kwargs):
            start = time.process_time()
            result = func(*args, **kwargs)
            Bmark._last_time = time.process_time() - start
            return result

        return wrapper

    @staticmethod
    def disabled_garbage(func):
        def wrapper(*args, **kwargs):

            gc_old = gc.isenabled()
            gc.disable()

            result = func(*args, **kwargs)

            if gc_old:
                gc.enable()
            return result

        return wrapper

    @staticmethod
    def accumulate_to_total_time(func, set_last=False):
        @Bmark.disabled_garbage
        def wrapper(*args, **kwargs):

            start = time.process_time()
            result = func(*args, **kwargs)
            measurement = time.process_time() - start

            Bmark._total_time += measurement

            if set_last:
                Bmark._last_time = measurement

            return result

        return wrapper

    @staticmethod
    def accumulate_individual(func, set_last=False):
        @Bmark.disabled_garbage
        def wrapper(*args, **kwargs):

            start = time.process_time()
            result = func(*args, **kwargs)
            measurement = time.process_time() - start

            if set_last:
                Bmark._last_time = measurement

            if func not in Bmark._total_time_dict.keys():
                Bmark._total_time_dict[func] = 0

            Bmark._total_time_dict[func] += measurement

            return result

        return wrapper

    @staticmethod
    def get_acc_time():
        return Bmark._total_time

    @staticmethod
    def get_measured_time():
        return Bmark._last_time

    @staticmethod
    def get_all_acc_times():
        return Bmark._total_time_dict

    @staticmethod
    def reset_acc_time():
        Bmark._total_time = 0
