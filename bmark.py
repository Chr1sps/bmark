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
        """
        Disables garbage collecting during measuring a given function.
        """

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
        """
        Appends given measurement to a list under the func_id key.
        """
        if func_id not in Bmark._time_dict.keys():
            Bmark._time_dict[func_id] = []

        Bmark._time_dict[func_id].append(measurement)

    @staticmethod
    def _get_func_times(func_id: str) -> List[float] | None:
        """
        Returns a list of all measured function times if they exist, None
        otherwise.
        """
        if func_id not in Bmark._time_dict:
            return None

        return Bmark._time_dict[func_id]

    @staticmethod
    def _get_time_sum_func(func_id: str) -> float | None:
        """
        Returns a sum of all measurements of a given function if they exist,
        None otherwise.
        """
        if func_id not in Bmark._time_dict:
            return None

        return sum(Bmark._time_dict[func_id])

    @staticmethod
    def measure_time(*func_ids: str) -> Callable:
        """
        Time measurement decorator.

        Whenever the decorated function (or method) is called the decorator
        measures the time is takes to finish it. This decorator temporarily
        disables garbage collecting in order to get correct measurements.

        This decorator can have specified function ids as arguments. This will
        make the class associate all the measurements with the given ids
        (provided ``Bmark.enable_accumulating()`` has been called
        beforehand).
        """

        def decorator(func: Callable) -> Callable:
            @Bmark._disabled_garbage
            def wrapper(*args, **kwargs):

                start = time.process_time()
                result = func(*args, **kwargs)
                measurement = time.process_time() - start

                if Bmark._accumulate:
                    for func_id in func_ids:
                        Bmark._accumulate_to_dict(func_id, measurement)
                Bmark._last_time = measurement

                return result

            return wrapper

        return decorator

    @staticmethod
    def get_measured_time() -> float | None:
        """
        Returns the last measurement (``None`` if there was none or if
        ``Bmark.reset_measured_time()`` has been invoked).
        """
        return Bmark._last_time

    @staticmethod
    def get_times_funcs(
        func_id: str, *func_ids: str
    ) -> None | List[float] | Dict[str, None | List[float]]:

        if len(func_ids) == 0:
            return Bmark._get_func_times(func_id)

        else:
            result: Dict[str, None | List[float]] = {}
            result[func_id] = Bmark._get_func_times(func_id)

            for id in func_ids:
                result[id] = Bmark._get_func_times(id)

            return result

    @staticmethod
    def get_last_func_time(func_id: str) -> float | None:

        if func_id not in Bmark._time_dict:
            return None

        return Bmark._time_dict[func_id][-1]

    @staticmethod
    def get_time_sum_funcs(func_id: str, *func_ids: str) -> float | None:

        result = Bmark._get_time_sum_func(func_id)

        for id in func_ids:

            func_time = Bmark._get_time_sum_func(id)

            if func_time is not None:
                if result is None:
                    result = 0
                result += func_time

        return result

    @staticmethod
    def get_time_sum_all_funcs() -> float | None:

        if len(Bmark._time_dict) == 0:
            return None

        return Bmark.get_time_sum_funcs(*Bmark._time_dict.keys())

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
