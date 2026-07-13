import threading

# Thread-safe counter used to track skipped records during import operations.
class SkipCounter:
    def __init__(self):
        self._lock = threading.Lock()
        self._count = 0

    def increment(self):
        with self._lock:
            self._count += 1

    @property
    def total(self):
        return self._count