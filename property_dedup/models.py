from django.db import models


class PropertyDuplicateGroup(models.Model):
    group_id = models.CharField(max_length=36, db_index=True)
    property_id = models.CharField(max_length=20, unique=True)
    is_primary = models.BooleanField(default=False)
    matched_score = models.FloatField()
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "property_duplicate_groups"
        verbose_name = "Property Duplicate Group"
        verbose_name_plural = "Property Duplicate Groups"

    def __str__(self):
        role = "PRIMARY" if self.is_primary else "member"
        return f"[{self.group_id}] {self.property_id} ({role}, score={self.matched_score})"
