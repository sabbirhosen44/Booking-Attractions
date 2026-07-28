from duplicate_detection.union_find import UnionFind
from duplicate_detection.vector_source import VectorSource


# Builds duplicate pairs from vector similarity, no loops possible
class GroupingService:
    def __init__(self):
        self.vector_source = VectorSource()

    def build_groups(self) -> list:
        vectors = self.vector_source.load_all_vectors()
        neighbors = self.vector_source.find_neighbors(vectors)

        uf = UnionFind(list(vectors.keys()))
        for property_id, matches in neighbors.items():
            for matched_id, _ in matches:
                uf.union(property_id, matched_id)

        raw_groups = uf.groups()

        return [
            self._build_pair_rows(members, neighbors)
            for members in raw_groups.values()
            if len(members) > 1
        ]

    @staticmethod
    def _build_pair_rows(members: list, neighbors: dict) -> list:
        member_set = set(members)
        rows = []
        for property_id in members:
            for matched_id, score in neighbors.get(property_id, []):
                if matched_id in member_set:
                    rows.append({
                        "property_id": property_id,
                        "duplicate_id": matched_id,
                        "score": round(score, 6),
                    })
        return rows