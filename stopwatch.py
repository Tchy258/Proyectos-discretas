import time


class StopWatchError(Exception):
    """Exception to report errors in Timer class"""


class StopWatch:

    def __init__(self):
        self._start_time = None


    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            raise StopWatchError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()


    def stop(self):
        """Method used for stoping the timer and returning the elapsed time
        since .start() was called.
        """
        if self._start_time is None:
            raise StopWatchError(f"Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        return elapsed_time