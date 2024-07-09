import logging
import time


class Timer:
    def __init__(self, description="Execution time", logger=None, unit="seconds"):
        self.description = description
        self.logger = logger or self._default_logger()
        self.unit = unit
        self.start_time = None
        self.end_time = None

    def _default_logger(self):
        logger = logging.getLogger("Timer")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        elapsed_time = self.end_time - self.start_time
        if self.unit == "milliseconds":
            elapsed_time *= 1000
        elif self.unit == "minutes":
            elapsed_time /= 60
        self.logger.info(f"{self.description} takes {elapsed_time:.2f} {self.unit}")
