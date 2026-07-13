# Maintains a fixed-size in-memory batch before records are written to the database.

class BatchBuffer:
    def __init__(self, batch_size):
        self._batch_size = batch_size
        self._items = []

    def add(self, item):
        self._items.append(item)

    def is_full(self):
        return len(self._items) >= self._batch_size

    def items(self):
        return self._items

    def clear(self):
        self._items = []

    def __len__(self):
        return len(self._items)

    def __bool__(self):
        return bool(self._items)