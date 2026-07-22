import ijson
from pathlib import Path
from typing import Iterator


# Streams JSON array files one record at a time
class JsonReader:
    @staticmethod
    def iter_records(folder: Path, pattern: str = "**/*.json") -> Iterator[dict]:
        for file_path in sorted(folder.glob(pattern)):
            with open(file_path, "rb") as f:
                for record in ijson.items(f, "item"):
                    yield record
