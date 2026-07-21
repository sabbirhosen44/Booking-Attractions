import re
import unicodedata

from pyspark.sql.functions import udf
from pyspark.sql.types import StringType


# Pure-python slugify, no Django dependency
class SlugTransform:

    @staticmethod
    def _slugify(value):
        if not value:
            return None

        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
        value = re.sub(r"[^\w\s-]", "", value).strip().lower()
        value = re.sub(r"[-\s]+", "-", value)

        return value[:150] or None

    @classmethod
    def udf(cls):
        return udf(cls._slugify, StringType())
