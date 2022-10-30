import gc
import time
from typing import Callable, Dict, List, Optional

"""
A collection of benchmark functions useful in data science applications
"""
_last_time: Optional[float] = None
_time_dict: Dict[str, List[float]] = {}
_accumulate = False


def _disabled_garbage(func: Callable):
    """
    Disables garbage collecting when measuring a given function.
    """

    def wrapper(*args, **kwargs):
        gc_old = gc.isenabled()
        gc.disable()
        result = func(*args, **kwargs)
        if gc_old:
            gc.enable()
        return result

    return wrapper


def _accumulate_to_dict(func_id: str, measurement: float):
    """
    Appends given measurement to a list under the func_id key.
    """
    if func_id not in _time_dict.keys():
        _time_dict[func_id] = []
    _time_dict[func_id].append(measurement)


def _get_func_times(func_id: str) -> Optional[List[float]]:
    """
    Returns a list of all measured function times if they exist, None
    otherwise.
    """
    if func_id not in _time_dict:
        return None
    return _time_dict[func_id]


def _get_time_sum_func(func_id: str) -> Optional[float]:
    """
    Returns a sum of all measurements of a given function if they exist,
    None otherwise.
    """
    if func_id not in _time_dict:
        return None
    return sum(_time_dict[func_id])


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
        @_disabled_garbage
        def wrapper(*args, **kwargs):
            start = time.process_time()
            result = func(*args, **kwargs)
            measurement = time.process_time() - start
            if _accumulate:
                for func_id in func_ids:
                    _accumulate_to_dict(func_id, measurement)
            global _last_time
            _last_time = measurement
            return result

        return wrapper

    return decorator


def get_measured_time() -> Optional[float]:
    """
    Returns the last measurement (``None`` if there was none or if
    ``reset_measured_time()`` has been invoked).
    """
    return _last_time


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
        return _get_func_times(func_id)
    else:
        result: Dict[str, None | List[float]] = {}
        result[func_id] = _get_func_times(func_id)
        for id in func_ids:
            result[id] = _get_func_times(id)
        return result


def get_last_func_time(func_id: str) -> Optional[float]:
    """
    Returns the last measurement performed on a function (or ``None`` if
    there are no such measurements).
    """
    if func_id not in _time_dict:
        return None
    return _time_dict[func_id][-1]


def get_time_sum_funcs(func_id: str, *func_ids: str) -> Optional[float]:
    """
    Returns a sum of all measurements of all functions given as parameters
    (or ``None`` if none of the functions has any measurements).
    """
    _remaining_ids = list(_time_dict.keys())
    result = _get_time_sum_func(func_id)
    try:
        _remaining_ids.remove(func_id)
    except ValueError:
        result = None
    for id in func_ids:
        func_time = _get_time_sum_func(id)
        try:
            _remaining_ids.remove(id)
        except ValueError:
            func_time = None
        if func_time is not None:
            if result is None:
                result = 0
            result += func_time
    del _remaining_ids
    return result


def get_time_sum_all_funcs() -> Optional[float]:
    """
    Returns a sum of all measurements of all functions (or ``None`` if none
    of the functions has any measurements).
    """
    if len(_time_dict) == 0:
        return None
    return get_time_sum_funcs(*_time_dict.keys())


def enable_accumulating():
    """Enables storing all performed measurements to an inner dict."""
    global _accumulate
    _accumulate = True


def disable_accumulating():
    """Disables storing all performed measurements to an inner dict."""
    global _accumulate
    _accumulate = False


def reset_measured_time():
    """
    Resets last measured time. After this call, ``get_measured_time``
    will return None.
    """
    global _last_time
    _last_time = None


def _reset_func_times(func_id: str):
    """Resets all stored measurements of a given function."""
    if func_id in _time_dict.keys():
        _time_dict.pop(func_id)


def reset_func_times(func_id: str, *func_ids: str):
    """
    Resets all stored measurements of all functions given as
    parameters.
    """
    _reset_func_times(func_id)
    for id in func_ids:
        _reset_func_times(id)


def reset_all_func_times():
    """Resets all stored measurements of all functions."""
    _time_dict.clear()


def reset_to_default():
    reset_all_func_times()
    reset_measured_time()
    disable_accumulating()
