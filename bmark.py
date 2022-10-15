import gc
import time


class Bmark:
    """
    A collection of benchmark functions useful in data science applications
    """

    _total_time = 0
    _last_time = None
    _total_time_dict = {}

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
        if set_last:

            @Bmark.disabled_garbage
            def wrapper(*args, **kwargs):
                start = time.process_time()
                result = func(*args, **kwargs)
                Bmark._last_time = time.process_time() - start
                Bmark._total_time += Bmark._last_time
                return result

        else:

            @Bmark.disabled_garbage
            def wrapper(*args, **kwargs):
                start = time.process_time()
                result = func(*args, **kwargs)
                Bmark._total_time += time.process_time() - start
                return result

        return wrapper

    @staticmethod
    def accumulate_individual(func, set_last=False):
        if set_last:

            @Bmark.disabled_garbage
            def wrapper(*args, **kwargs):
                start = time.process_time()
                result = func(*args, **kwargs)
                Bmark._last_time = time.process_time() - start
                if func not in Bmark._total_time_dict.keys():
                    Bmark._total_time_dict[func] = 0
                Bmark._total_time_dict[func] += Bmark._last_time
                return result

        else:

            @Bmark.disabled_garbage
            def wrapper(*args, **kwargs):
                start = time.process_time()
                result = func(*args, **kwargs)
                if func not in Bmark._total_time_dict.keys():
                    Bmark._total_time_dict[func] = 0
                Bmark._total_time_dict[func] += time.process_time() - start
                return result

        return wrapper

    @staticmethod
    def get_acc_time():
        return Bmark._total_time

    @staticmethod
    def get_measured_time():
        return Bmark._last_time

    @staticmethod
    def reset_acc_time():
        Bmark._total_time = 0
