class PriceSegmentTransformer:

    def transform(self, price):
        if price is None:
            return "void"

        if price < 200:
            return "segments 1"

        if price < 500:
            return "segments 2"

        if price < 1000:
            return "segments 3"

        if price < 5000:
            return "segments 4"

        return "segments 5"