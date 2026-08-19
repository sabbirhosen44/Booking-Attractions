class ValueNormalizer:

    VOID = "void"

    @classmethod
    def normalize(cls, value):
        if value is None:
            return cls.VOID

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return cls.VOID

        return str(value)