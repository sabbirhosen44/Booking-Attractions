from duplicate_detection.models import PropertyDuplicateGroup


# Replaces all duplicate pair rows with a fresh detection result
class GroupWriter:
    @staticmethod
    def write(groups: list) -> int:
        PropertyDuplicateGroup.objects.all().delete()

        rows = [
            PropertyDuplicateGroup(**row)
            for group in groups
            for row in group
        ]
        PropertyDuplicateGroup.objects.bulk_create(rows, batch_size=500)
        return len(rows)