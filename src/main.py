import pandas as pd
import random
import time
import matplotlib.pyplot as plt
import numpy as np
import os

HASH_TABLE_SIZE = 50000
NUM_QUERIES_LIST = [100, 500, 1000, 2000, 3000, 5000]
SEARCH_PATTERNS = ['random', 'sequential', 'clustered', 'mixed', 'missing']

class HashIndex:
    def __init__(self, size):
        self.size = size
        self.table = [[] for _ in range(size)]
        self.collisions = 0

    def _hash(self, key):
        return hash(key) % self.size

    def insert(self, key, value):
        idx = self._hash(key)
        if self.table[idx]:
            self.collisions += 1
        self.table[idx].append((key, value))

    def search(self, key):
        idx = self._hash(key)
        for k, v in self.table[idx]:
            if k == key:
                return v
        return None

def linear_search(data, key):
    for record in data:
        if record[0] == key:
            return record
    return None

def generate_keys(data_ids, pattern, num_queries):
    if pattern == 'random':
        return random.sample(data_ids, num_queries)
    elif pattern == 'sequential':
        return data_ids[:num_queries]
    elif pattern == 'clustered':
        start = random.randint(0, len(data_ids) - num_queries)
        return data_ids[start:start + num_queries]
    elif pattern == 'mixed':
        return [random.choice(data_ids) if i % 2 == 0 else data_ids[i % len(data_ids)] for i in range(num_queries)]
    elif pattern == 'missing':
        return [f"MISSING_{i}" for i in range(num_queries)]
    return []

def benchmark_search_times(method, structure, keys):
    times = []
    for key in keys:
        start = time.time()
        method(structure, key)
        times.append((time.time() - start) * 1000)  # ms
    return times

def main():
    df = pd.read_csv('../data/pricerunner_aggregate.csv')
    df.columns = [col.strip().replace(" ","_") for col in df.columns]
    data = list(zip(df['Product_ID'], df['Product_Title']))
    product_ids = list(df['Product_ID'])

    # Build hash index
    index = HashIndex(HASH_TABLE_SIZE)
    start = time.time()
    for pid, title in data:
        index.insert(pid, title)
    insertion_time = time.time() - start

    print(f"\nInserted {len(data)} records in {insertion_time:.4f} seconds.")
    print(f"Total collisions: {index.collisions}\n")

    # Store results for stats and plotting
    records = []

    for num_queries in NUM_QUERIES_LIST:
        for pattern in SEARCH_PATTERNS:
            keys = generate_keys(product_ids, pattern, num_queries)

            # Get raw times for hash index
            hash_times = benchmark_search_times(HashIndex.search, index, keys)
            # Get raw times for linear search
            linear_times = benchmark_search_times(linear_search, data, keys)

            hash_avg = np.mean(hash_times)
            hash_std = np.std(hash_times)

            linear_avg = np.mean(linear_times)
            linear_std = np.std(linear_times)

            speedup = linear_avg / hash_avg if hash_avg else float('inf')

            records.append({
                'queries': num_queries,
                'pattern': pattern,
                'hash_avg': hash_avg,
                'hash_std': hash_std,
                'hash_times': hash_times,
                'linear_avg': linear_avg,
                'linear_std': linear_std,
                'linear_times': linear_times,
                'speedup': speedup
            })

            print(f"[{pattern.capitalize()} | {num_queries} queries] Hash: {hash_avg:.4f} ms, Linear: {linear_avg:.4f} ms")

    results_df = pd.DataFrame(records)
    os.makedirs("../results", exist_ok=True)
    results_df.to_csv("../results/performance.csv", index=False)

    # ---------- PLOTTING ---------- #

    # 1) Average time per search by pattern (Hash & Linear)
    plt.figure(figsize=(10,6))
    for pattern in SEARCH_PATTERNS:
        subset = results_df[results_df['pattern'] == pattern]
        plt.plot(subset['queries'], subset['hash_avg'], marker='o', label=f'Hash - {pattern}')
        plt.plot(subset['queries'], subset['linear_avg'], marker='x', linestyle='--', label=f'Linear - {pattern}')
    plt.title('Average Search Time by Pattern')
    plt.xlabel('Number of Searches')
    plt.ylabel('Average Search Time (ms)')
    plt.legend()
    plt.grid(True)
    plt.savefig("../results/avg_search_time_by_pattern.png")
    plt.clf()

    # 2) Boxplot of Hash Index mean search times by pattern using matplotlib only
    plt.figure(figsize=(10, 6))
    data_to_plot = []
    labels = []
    for pattern in SEARCH_PATTERNS:
        vals = results_df[results_df['pattern'] == pattern]['hash_avg'].values
        data_to_plot.append(vals)
        labels.append(pattern)
    plt.boxplot(data_to_plot, labels=labels)
    plt.title('Boxplot of Hash Index Mean Search Times by Pattern')
    plt.ylabel('Mean Search Time (ms)')
    plt.xlabel('Pattern')
    plt.grid(True)
    plt.savefig("../results/hash_boxplot_mean_search_times.png")
    plt.clf()

    # 3) Hash index: std search time by pattern (line plot)
    plt.figure(figsize=(10,6))
    for pattern in SEARCH_PATTERNS:
        subset = results_df[results_df['pattern'] == pattern]
        plt.plot(subset['queries'], subset['hash_std'], marker='s', label=f'{pattern}')
    plt.title('Hash Index Standard Deviation of Search Times by Pattern')
    plt.xlabel('Number of Searches')
    plt.ylabel('Std Dev of Search Time (ms)')
    plt.legend()
    plt.grid(True)
    plt.savefig("../results/hash_std_search_time.png")
    plt.clf()

    # 4) Linear search: min and max search time by pattern (bar plots)
    min_times = []
    max_times = []
    for pattern in SEARCH_PATTERNS:
        all_linear_times = []
        for times_list in results_df[results_df['pattern'] == pattern]['linear_times']:
            all_linear_times.extend(times_list)
        min_times.append(min(all_linear_times))
        max_times.append(max(all_linear_times))

    plt.figure(figsize=(10,5))
    plt.bar(SEARCH_PATTERNS, min_times, color='skyblue')
    plt.title('Min Linear Search Time by Pattern')
    plt.ylabel('Min Search Time (ms)')
    plt.savefig("../results/linear_search_min_time_by_pattern.png")
    plt.clf()

    plt.figure(figsize=(10,5))
    plt.bar(SEARCH_PATTERNS, max_times, color='salmon')
    plt.title('Max Linear Search Time by Pattern')
    plt.ylabel('Max Search Time (ms)')
    plt.savefig("../results/linear_search_max_time_by_pattern.png")
    plt.clf()

    # 5) Linear search: mean and std search time by pattern (line plot)
    plt.figure(figsize=(10,6))
    for pattern in SEARCH_PATTERNS:
        subset = results_df[results_df['pattern'] == pattern]
        plt.plot(subset['queries'], subset['linear_avg'], marker='o', label=f'{pattern}')
        plt.fill_between(subset['queries'],
                         subset['linear_avg'] - subset['linear_std'],
                         subset['linear_avg'] + subset['linear_std'], alpha=0.2)
    plt.title('Linear Search Mean and Std Dev by Pattern')
    plt.xlabel('Number of Searches')
    plt.ylabel('Search Time (ms)')
    plt.legend()
    plt.grid(True)
    plt.savefig("../results/linear_mean_std_search_time.png")
    plt.clf()

    # 6) Log-log plot: search performance scaling (Linear & Hash)
    plt.figure(figsize=(10,6))
    for pattern in SEARCH_PATTERNS:
        subset = results_df[results_df['pattern'] == pattern]
        plt.loglog(subset['queries'], subset['linear_avg'], label=f'Linear - {pattern}', linestyle='--')
        plt.loglog(subset['queries'], subset['hash_avg'], label=f'Hash - {pattern}')
    plt.title('Log-Log Plot: Search Time Scaling with Number of Searches')
    plt.xlabel('Number of Searches (log scale)')
    plt.ylabel('Avg Search Time (ms) (log scale)')
    plt.legend()
    plt.grid(True, which='both', ls='--')
    plt.savefig("../results/loglog_search_scaling.png")
    plt.clf()

    print("\n✅ All graphs saved to '../results' folder.")

if __name__ == "__main__":
    main()
