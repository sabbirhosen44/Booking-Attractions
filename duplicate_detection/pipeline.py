from duplicate_detection.grouping_service import GroupingService
from duplicate_detection.writer import GroupWriter


# Runs duplicate detection end to end
class DuplicateDetectionRunner:
    def run(self):
        print("Loading vectors and searching for matches...")
        groups = GroupingService().build_groups()

        print(f"Found {len(groups)} duplicate groups.")
        row_count = GroupWriter.write(groups)

        print(f"Wrote {row_count} rows into property_duplicate_groups.")
