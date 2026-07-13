import os
from pathlib import Path
from core.configuration import (
    BASE_DIR,
    IMPORT,
)


# Centralizes import-related configuration values used across all import services.
class ImportConfig:
    DATA_DIR = (
        Path(BASE_DIR)
        / IMPORT["data_dir"]
    )
    BATCH_SIZE = 1000
    MAX_WORKERS = min(8, os.cpu_count() or 4)