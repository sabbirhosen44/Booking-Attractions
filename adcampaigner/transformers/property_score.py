from bisect import bisect_right


class PropertyScoreTransformer:

    def __init__(self, price_scores):
        self.price_scores = sorted(
            float(score)
            for score in price_scores
            if score is not None
        )

    def transform(self, price):
        if price is None:
            return "void"

        try:
            price = float(price)
        except (TypeError, ValueError):
            return "void"

        if not self.price_scores:
            return "void"

        index = bisect_right(self.price_scores, price)

        if index >= len(self.price_scores) - 1:
            return "void"

        return self.price_scores[index + 1]