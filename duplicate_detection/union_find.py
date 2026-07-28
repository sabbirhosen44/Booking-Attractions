# Groups properties by similarity with no possible loops
class UnionFind:
    def __init__(self, items: list):
        self.parent = {item: item for item in items}

    def find(self, item):
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, a, b):
        root_a, root_b = self.find(a), self.find(b)
        if root_a != root_b:
            self.parent[root_b] = root_a

    def groups(self) -> dict:
        result = {}
        for item in self.parent:
            root = self.find(item)
            result.setdefault(root, []).append(item)
        return result
