import re
import unicodedata

from pyspark.sql.types import StringType
from pyspark.sql.functions import udf


# Pure-python slugify (no Django dependency, keeps this decoupled from Django)
def _slugify(value):
    if not value:
        return None

    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    value = re.sub(r"[-\s]+", "-", value)

    return value[:150] or None


slugify_udf = udf(_slugify, StringType())
