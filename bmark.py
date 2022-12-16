"""
A collection of benchmark functions useful in data science applications
"""
import contextlib
import gc
import time
from typing import Callable, Dict, List, Optional

import numpy as np

__last_time: Optional[float] = None
__time_dict: Dict[str, List[float]] = {}
__accumulate: bool = False
__gc_disabled: bool = True


def __disabled_garbage(func: Callable):
    """
    Disables garbage collecting when measuring a given function.
    """

    def wrapper(*args, **kwargs):
        gc_old = None  # silence unbound warning
        if __gc_disabled:
            gc_old = gc.isenabled()
            gc.disable()
        result = func(*args, **kwargs)
        if __gc_disabled:
            if gc_old:
                gc.enable()
        return result

    return wrapper


def __accumulate_to_dict(func_id: str, measurement: float):
    """
    Appends given measurement to a list under the func_id key.
    """
    if func_id not in __time_dict.keys():
        __time_dict[func_id] = []
    __time_dict[func_id].append(measurement)


def __get_func_times(func_id: str) -> Optional[List[float]]:
    """
    Returns a list of all measured function times if they exist, None
    otherwise.
    """
    if func_id not in __time_dict:
        return None
    return __time_dict[func_id]


def __get_time_sum_func(func_id: str) -> Optional[float]:
    """
    Returns a sum of all measurements of a given function if they exist,
    None otherwise.
    """
    if func_id not in __time_dict:
        return None
    return sum(__time_dict[func_id])


def measure_time(*func_ids: str) -> Callable:
    """
    Time measurement decorator.
    Whenever the decorated function (or method) is called the decorator
    measures the time is takes to finish it. This decorator temporarily
    disables garbage collecting in order to get correct measurements.
    This decorator can have specified function ids as arguments. This will
    make the class associate all the measurements with the given ids
    (provided ``enable_accumulating()`` has been called
    beforehand).
    """

    def decorator(func: Callable) -> Callable:
        @__disabled_garbage
        def wrapper(*args, **kwargs):
            start = time.process_time()
            result = func(*args, **kwargs)
            measurement = time.process_time() - start
            if __accumulate:
                for func_id in func_ids:
                    __accumulate_to_dict(func_id, measurement)
            global __last_time
            __last_time = measurement
            return result

        return wrapper

    return decorator


def get_measured_time() -> Optional[float]:
    """
    Returns the last measurement (``None`` if there was none or if
    ``reset_measured_time()`` has been invoked).
    """
    return __last_time


def get_times_funcs(
    func_id: str, *func_ids: str
) -> None | List[float] | Dict[str, None | List[float]]:
    """
    If a single function id is given, returns a list of all measurements of
    the function if exists, ``None`` otherwise. If instead multiple ids are
    given, returns a dictionary with function ids as keys and similar lists
    as values (with all measurements of each function accordingly, ``None``
    if there are no such measurements).
    """
    if len(func_ids) == 0:
        return __get_func_times(func_id)
    else:
        result: Dict[str, None | List[float]] = {}
        result[func_id] = __get_func_times(func_id)
        for id in func_ids:
            result[id] = __get_func_times(id)
        return result


def get_last_func_time(func_id: str) -> Optional[float]:
    """
    Returns the last measurement performed on a function (or ``None`` if
    there are no such measurements).
    """
    if func_id not in __time_dict:
        return None
    return __time_dict[func_id][-1]


def get_time_sum_funcs(func_id: str, *func_ids: str) -> Optional[float]:
    """
    Returns a sum of all measurements of all functions given as parameters
    (or ``None`` if none of the functions has any measurements).
    """
    __remaining_ids = list(__time_dict.keys())
    result = __get_time_sum_func(func_id)
    try:
        __remaining_ids.remove(func_id)
    except ValueError:
        result = None
    for id in func_ids:
        func_time = __get_time_sum_func(id)
        try:
            __remaining_ids.remove(id)
        except ValueError:
            func_time = None
        if func_time is not None:
            if result is None:
                result = 0
            result += func_time
    del __remaining_ids
    return result


def get_time_sum_all_funcs() -> Optional[float]:
    """
    Returns a sum of all measurements of all functions (or ``None`` if none
    of the functions has any measurements).
    """
    if len(__time_dict) == 0:
        return None
    return get_time_sum_funcs(*__time_dict.keys())


def set_accumulating(do_acc: bool):
    global __accumulate
    __accumulate = do_acc


def set_disabled_gc(disabled: bool):
    global __gc_disabled
    __gc_disabled = disabled


def reset_measured_time():
    """
    Resets last measured time. After this call, ``get_measured_time``
    will return None.
    """
    global __last_time
    __last_time = None


def __reset_func_times(func_id: str):
    """Resets all stored measurements of a given function."""
    if func_id in __time_dict.keys():
        __time_dict.pop(func_id)


def reset_func_times(func_id: str, *func_ids: str):
    """
    Resets all stored measurements of all functions given as
    parameters.
    """
    __reset_func_times(func_id)
    for id in func_ids:
        __reset_func_times(id)


def reset_all_func_times():
    """Resets all stored measurements of all functions."""
    __time_dict.clear()


def reset_to_default():
    """
    Resets the module to default state (no measurements, disabled
    accumulating).
    """
    reset_all_func_times()
    reset_measured_time()
    set_accumulating(False)


@contextlib.contextmanager
@__disabled_garbage
def measure_block(*func_ids: str):
    """
    Context manager equivalent for the bmark.measure_time decorator.
    """
    start = time.process_time()
    try:
        yield
    finally:
        measurement = time.process_time() - start
        global __last_time, __accumulate
        __last_time = measurement
        if __accumulate:
            for func_id in func_ids:
                __accumulate_to_dict(func_id, measurement)


def get_percentile(
    func_id: str, percentile: float, interpolate: bool = False
) -> float:
    method = "lower"
    if interpolate:
        method = "linear"
    return np.percentile(
        __time_dict[func_id], percentile, method=method
    )  # type: ignore


def get_average(func_id: str) -> float:
    return np.average(__time_dict[func_id])  # type: ignore


def get_median(func_id: str) -> float:
    return np.median(__time_dict[func_id])  # type: ignore


def get_std_dev(func_id: str) -> float:
    return np.std(__time_dict[func_id])  # type: ignore
