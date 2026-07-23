# DynamoDB only needs key attributes defined up front, not every field.
# Tables with a real id use it as partition key.
# Tables with no real id use property_id + a sort key that makes each
# item unique (same role the missing id column plays in the other two
# pipelines).

TABLE_SCHEMAS = {
    "rental_property": {
        "key_schema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "attribute_definitions": [{"AttributeName": "id", "AttributeType": "S"}],
    },
    "rental_property_localize": {
        "key_schema": [
            {"AttributeName": "property_id", "KeyType": "HASH"},
            {"AttributeName": "language_country_code", "KeyType": "RANGE"},
        ],
        "attribute_definitions": [
            {"AttributeName": "property_id", "AttributeType": "S"},
            {"AttributeName": "language_country_code", "AttributeType": "S"},
        ],
    },
    "property_image_meta": {
        "key_schema": [
            {"AttributeName": "property_id", "KeyType": "HASH"},
            {"AttributeName": "url", "KeyType": "RANGE"},
        ],
        "attribute_definitions": [
            {"AttributeName": "property_id", "AttributeType": "S"},
            {"AttributeName": "url", "AttributeType": "S"},
        ],
    },
    "property_reviews": {
        "key_schema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "attribute_definitions": [{"AttributeName": "id", "AttributeType": "S"}],
    },
    "price_history": {
        "key_schema": [
            {"AttributeName": "property_id", "KeyType": "HASH"},
            {"AttributeName": "created_at", "KeyType": "RANGE"},
        ],
        "attribute_definitions": [
            {"AttributeName": "property_id", "AttributeType": "S"},
            {"AttributeName": "created_at", "AttributeType": "S"},
        ],
    },
    "skip_properties": {
        "key_schema": [{"AttributeName": "property_id", "KeyType": "HASH"}],
        "attribute_definitions": [{"AttributeName": "property_id", "AttributeType": "S"}],
    },
}