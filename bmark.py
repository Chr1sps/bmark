import gc
import time
from typing import Callable, Dict, List


class Bmark:
    """
    A collection of benchmark functions useful in data science applications
    """

    _last_time: float | None = None
    _time_dict: Dict[Callable, List[float]] = {}
    _accumulate = False

    @staticmethod
    def _disabled_garbage(func):
        def wrapper(*args, **kwargs):

            gc_old = gc.isenabled()
            gc.disable()

            result = func(*args, **kwargs)

            if gc_old:
                gc.enable()
            return result

        return wrapper

    @staticmethod
    def _accumulate_to_dict(func, measurement):
        if func not in Bmark._time_dict.keys():
            Bmark._time_dict[func] = []
        Bmark._time_dict[func].append(measurement)

    @staticmethod
    def measure_time(func) -> Callable:
        @Bmark._disabled_garbage
        def wrapper(*args, **kwargs):

            start = time.process_time()
            result = func(*args, **kwargs)
            measurement = time.process_time() - start

            if Bmark._accumulate:
                Bmark._accumulate_to_dict(func, measurement)
            Bmark._last_time = measurement

            return result

        return wrapper

    @staticmethod
    def get_measured_time() -> float:
        return Bmark._last_time

    @staticmethod
    def get_func_times(func: Callable) -> List[float]:
        if func not in Bmark._time_dict:
            return None
        return Bmark._time_dict[func]

    @staticmethod
    def get_last_func_time(func: Callable) -> float:
        if func not in Bmark._time_dict:
            return None
        return Bmark._time_dict[func][-1]

    @staticmethod
    def get_time_sum_func(func: Callable) -> float:
        if func not in Bmark._time_dict.keys():
            return None
        return sum(Bmark._time_dict[func])

    @staticmethod
    def get_time_sum_all_funcs() -> float:
        return sum(sum(list) for list in Bmark._time_dict.items())

    @staticmethod
    def enable_accumulating():
        Bmark._accumulate = True

    @staticmethod
    def disable_accumulating():
        Bmark._accumulate = False

    @staticmethod
    def reset_measured_time():
        Bmark._last_time = None

    @staticmethod
    def delete_func_times(func):
        if func in Bmark._time_dict.keys():
            Bmark._time_dict.pop(func)

    @staticmethod
    def delete_all_func_times():
        Bmark._time_dict.clear()
