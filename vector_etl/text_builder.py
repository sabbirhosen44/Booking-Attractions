# Builds one descriptive text blob per attraction, used for embedding
class TextBuilder:
    @staticmethod
    def build(record: dict, city_name: str, country_code: str) -> str:
        name_map = record.get("name") or {}
        property_name = name_map.get("en-us") or (next(iter(name_map.values()), None)) or record["id"]
        categories = record.get("categories") or []
        loc = (record.get("locations") or [{}])[0]
        address = loc.get("address") or ""

        parts = [
            property_name,
            f"located in {city_name}, {country_code}" if city_name else "",
            f"categories: {', '.join(categories)}" if categories else "",
            address,
        ]
        return ". ".join(p for p in parts if p)
    
    @staticmethod
    def build_from_row(row: dict) -> str:
        property_name = row.get("property_name") or row.get("id")
        city_name = row.get("city")
        country_code = row.get("country_code")
        categories = row.get("activity_categories") or []
        address = row.get("display") or ""

        parts = [
            property_name,
            f"located in {city_name}, {country_code}" if city_name else "",
            f"categories: {', '.join(categories)}" if categories else "",
            address,
        ]
        return ". ".join(p for p in parts if p)
