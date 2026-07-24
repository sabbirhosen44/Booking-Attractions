import uuid

NAMESPACE = uuid.UUID("12345678-1234-5678-1234-567812345678")

class PointId:
    @staticmethod 
    def for_property(property_id:str)->str:
        return str(uuid.uuid5(NAMESPACE,property_id))