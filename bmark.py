"""
# BMark

A collection of benchmark functions useful in data science applications
"""
import gc
import time
from typing import Callable, Dict, List, Optional

import numpy as np

__all__ = [
    "average",
    "clear_last_time",
    "clear_times",
    "disabled_gc",
    "get_last_time",
    "get_time_sum",
    "get_times",
    "measure_time",
    "MeasureBlock",
    "median",
    "percentile",
    "restore_defaults",
    "set_accumulating",
    "set_disabled_gc",
    "std_dev",
]

_accumulate: bool = True
_gc_disabled: bool = True
_last_time: Optional[float] = None
_time_dict: Dict[str, List[float]] = {}


# helper functions
def _turn_gc_off() -> bool:
    gc_old = False
    if _gc_disabled:
        gc_old = gc.isenabled()
        gc.disable()
    return gc_old


def _turn_gc_on(gc_old):
    if _gc_disabled:
        if gc_old:
            gc.enable()


def _disabled_garbage(func: Callable):
    """
    Disables garbage collecting when measuring a given function.
    """

    def wrapper(*args, **kwargs):
        gc_old = _turn_gc_off()
        result = func(*args, **kwargs)
        _turn_gc_on(gc_old)
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


def _get_time_sum(func_id: str) -> Optional[float]:
    """
    Returns a sum of all measurements of a given function if they exist,
    None otherwise.
    """
    if func_id not in _time_dict:
        return None
    return sum(_time_dict[func_id])


# main measurement tools
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


class MeasureBlock:
    """
    When used in a ``with`` statement, this class measures time for a set of
    ids defined in it's constructor from the moment the ``with`` block has
    been initialized to the moment it terminates. Additionally, when used with
    the ``as`` keyword, the created object provides a set of functions useful
    for measuring time within the block with regards to the moment the block
    was called. This class is not meant to be used outside of the ``with``
    statement.
    """

    def __init__(self, *func_ids: str):
        """ """
        self._func_ids = func_ids

    def elapsed(self) -> float:
        """
        Returns the time since the context block has been initialized. Raises
        ``ValueError`` if the function is called outside of the ``with`` block.
        """
        try:
            return time.process_time() - self._start
        except AttributeError:
            raise AttributeError("Measure block was not started beforehand.")

    def period(self) -> float:
        """
        Upon first call of this method, returns the time since the context
        block has been initialized. Afterwards, returns the time since the last
        call of this method. Raises ``ValueError`` if the function is called
        outside of the ``with`` block.
        """
        try:
            current_time = time.process_time()
            result = current_time - self._period_start
            self._period_start = current_time
            return result
        except AttributeError:
            raise AttributeError("Measure block was not started beforehand.")

    def __enter__(self) -> "MeasureBlock":
        self._gc_old = _turn_gc_off()
        self._start = self._period_start = time.process_time()
        return self

    def __exit__(self, r_type, r_value, r_traceback):
        measurement = time.process_time() - self._start
        global _accumulate, _last_time
        _last_time = measurement
        if _accumulate:
            for func_id in self._func_ids:
                _accumulate_to_dict(func_id, measurement)
        _turn_gc_on(self._gc_old)


# time retrieval functions
def get_last_time(func_id: Optional[str] = None) -> Optional[float]:
    """
    If func_id is None, returns the overall last measured time of all
    functions. Otherwise, returns the last measured time of a given function.
    """
    if func_id is None:
        return _last_time
    else:
        if func_id not in _time_dict:
            return None
        return _time_dict[func_id][-1]


def get_times(
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
        result: Dict[str, None | List[float]] = {
            func_id: _get_func_times(func_id)
        }
        for id_ in func_ids:
            result[id_] = _get_func_times(id_)
        return result


def get_time_sum(*func_ids: str) -> Optional[float]:
    """
    If no ids are specified, returns the sum of all times of all ids.
    Otherwise, returns the joint sum of all times of all ids specified.
    """
    if len(func_ids) == 0:
        if len(_time_dict) == 0:
            return None
        else:
            return sum([sum(v) for v in _time_dict.values()])
    else:
        result = None
        _remaining_ids = list(_time_dict.keys())
        for func_id in func_ids:
            func_time = _get_time_sum(func_id)
            try:
                _remaining_ids.remove(func_id)
            except ValueError:
                func_time = None
            if func_time is not None:
                if result is None:
                    result = 0
                result += func_time
        del _remaining_ids
        return result


# bmark options
def set_accumulating(do_acc: bool):
    """
    Sets if the measured values for each id are being accumulated (yes if
    ``True``, no if ``False``).
    """
    global _accumulate
    _accumulate = do_acc


def set_disabled_gc(disabled: bool):
    global _gc_disabled
    _gc_disabled = disabled


def disabled_gc():
    """
    Returns ``True`` if garbage collection is disabled upon benchmarking using
    either through the ``measure_time`` decorator of ``MeasureBlock`` context
    manager.
    """
    return _gc_disabled


# time deletion
def clear_last_time():
    """
    Resets last measured time. After this call, ``get_measured_time``
    will return None.
    """
    global _last_time
    _last_time = None


def _clear_times(func_id: str):
    """Resets all stored measurements of a given function."""
    if func_id in _time_dict.keys():
        _time_dict.pop(func_id)


def clear_times(*func_ids: str):
    """
    If no identifiers were passed, deletes times of all functions. Otherwise,
    deletes times associated with passed identifiers.
    """
    if len(func_ids) == 0:
        _time_dict.clear()
    else:
        for func_id in func_ids:
            _clear_times(func_id)


def restore_defaults():
    """
    Resets the module to default settings (no measurements, disabled
    accumulating).
    """
    clear_times()
    clear_last_time()
    set_accumulating(True)
    set_disabled_gc(True)


# statistical analysis
def percentile(
    func_id: str, percentile: float, interpolate: bool = False
) -> float:
    """
    Returns the given percentile of times under a given id. If interpolate is
    set to ``True``, percentiles will be interpolated to compensate for gaps
    between timings.
    """
    method = "lower"
    if interpolate:
        method = "linear"
    return float(np.percentile(_time_dict[func_id], percentile, method=method))


def average(func_id: str) -> float:
    """
    Returns the average of times under a given id.
    """
    return float(np.average(_time_dict[func_id]))


def median(func_id: str) -> float:
    """
    Returns the median of times under a given id.
    """
    return float(np.median(_time_dict[func_id]))


def std_dev(func_id: str) -> float:
    """
    Returns the standard deviation of times under a given id.
    """
    return float(np.std(_time_dict[func_id]))
