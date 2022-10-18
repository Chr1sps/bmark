import gc
import time
from typing import Callable, Dict, List


class Bmark:
    """
    A collection of benchmark functions useful in data science applications
    """

    _last_time: float | None = None
    _time_dict: Dict[str, List[float]] = {}
    _accumulate = False

    @staticmethod
    def _disabled_garbage(func: Callable):
        def wrapper(*args, **kwargs):

            gc_old = gc.isenabled()
            gc.disable()

            result = func(*args, **kwargs)

            if gc_old:
                gc.enable()
            return result

        return wrapper

    @staticmethod
    def _accumulate_to_dict(func_id: str, measurement: float):
        if func_id not in Bmark._time_dict.keys():
            Bmark._time_dict[func_id] = []
        Bmark._time_dict[func_id].append(measurement)

    @staticmethod
    def measure_time(func: Callable, func_id: str) -> Callable:
        @Bmark._disabled_garbage
        def wrapper(*args, **kwargs):

            start = time.process_time()
            result = func(*args, **kwargs)
            measurement = time.process_time() - start

            if Bmark._accumulate:
                Bmark._accumulate_to_dict(func_id, measurement)
            Bmark._last_time = measurement

            return result

        return wrapper

    @staticmethod
    def get_measured_time() -> float | None:
        return Bmark._last_time

    @staticmethod
    def get_func_times(func_id: str) -> List[float] | None:
        if func_id not in Bmark._time_dict:
            return None
        return Bmark._time_dict[func_id]

    @staticmethod
    def get_last_func_time(func_id: str) -> float | None:
        if func_id not in Bmark._time_dict:
            return None
        return Bmark._time_dict[func_id][-1]

    @staticmethod
    def get_time_sum_func(func_id: str) -> float | None:
        if func_id not in Bmark._time_dict.keys():
            return None
        return sum(Bmark._time_dict[func_id])

    @staticmethod
    def get_time_sum_all_funcs() -> float | None:
        result = None
        for func_id in Bmark._time_dict.keys():
            func_time = Bmark.get_time_sum_func(func_id)
            if func_time is not None:
                if result is None:
                    result = 0
                result += func_time
        return result

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
    def delete_func_times(func_id: str):
        if func_id in Bmark._time_dict.keys():
            Bmark._time_dict.pop(func_id)

    @staticmethod
    def delete_all_func_times():
        Bmark._time_dict.clear()
