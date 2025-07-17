import time
from collections import defaultdict

class HashIndex:
    def __init__(self, size):
        self.size = size
        self.table = defaultdict(list)
        self.collisions = 0

    def _hash(self, key):
        return hash(key) % self.size

    def insert(self, key, value):
        index = self._hash(key)
        # Check for collision
        if self.table[index]:
            self.collisions += 1
        self.table[index].append((key, value))

    def lookup(self, key):
        index = self._hash(key)
        for k, v in self.table[index]:
            if k == key:
                return v
        return None

    def batch_lookup(self, keys):
        total_time = 0
        for key in keys:
            start = time.perf_counter()
            self.lookup(key)
            end = time.perf_counter()
            total_time += (end - start)
        return total_time / len(keys) if keys else 0

    def get_collision_count(self):
        return self.collisions
