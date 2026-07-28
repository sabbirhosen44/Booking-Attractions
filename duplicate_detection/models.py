from django.db import models


class PropertyDuplicateGroup(models.Model):
    property_id = models.CharField(max_length=20, db_index=True)
    duplicate_id = models.CharField(max_length=20, db_index=True)
    score = models.FloatField()

    class Meta:
        db_table = "property_duplicate_groups"
        verbose_name, verbose_name_plural = "Property Duplicate", "Property Duplicates"
        constraints = [
            models.UniqueConstraint(
                fields=["property_id", "duplicate_id"],
                name="unique_property_duplicate_pair",
            ),
        ]
        indexes = [
            models.Index(fields=["property_id"]),
            models.Index(fields=["duplicate_id"]),
        ]