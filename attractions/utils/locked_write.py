import threading

from django.db import transaction

# Ensures database writes are executed inside a transaction and protected by a thread lock.
class LockedWrite:
    _lock = threading.Lock()

    def __enter__(self):
        self._lock.acquire()
        self._transaction = transaction.atomic()
        self._transaction.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            return self._transaction.__exit__(
                exc_type,
                exc_val,
                exc_tb,
            )
        finally:
            self._lock.release()