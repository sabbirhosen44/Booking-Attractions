import re


# Standalone slugify, no Django dependency
class SlugUtil:
    @staticmethod
    def slugify(value: str) -> str:
        if not value:
            return ""
        value = value.strip().lower()
        value = re.sub(r"[^\w\s-]", "", value)
        value = re.sub(r"[\s_]+", "-", value)
        return value.strip("-")[:150]
