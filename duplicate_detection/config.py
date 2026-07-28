from core.configuration import DUPLICATE_DETECTION


class DuplicateDetectionConfig:
    THRESHOLD = DUPLICATE_DETECTION.get("threshold", 0.95)
    QUERY_BATCH_SIZE = DUPLICATE_DETECTION.get("query_batch_size", 20)
    MAX_MATCHES_PER_PROPERTY = DUPLICATE_DETECTION.get("max_matches_per_property", 500)