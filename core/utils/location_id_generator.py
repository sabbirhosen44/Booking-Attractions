import secrets
import string


class LocationIDGenerator:

    PREFIX = "LC"
    ID_LENGTH = 10

    CHARACTERS = string.ascii_letters + string.digits

    @classmethod
    def generate(cls):
        suffix = "".join(
            secrets.choice(cls.CHARACTERS)
            for _ in range(cls.ID_LENGTH)
        )

        return f"{cls.PREFIX}{suffix}"