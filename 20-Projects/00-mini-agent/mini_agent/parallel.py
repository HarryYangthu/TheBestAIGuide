"""Lesson 06: real threads for independent reads, with deterministic merge order."""
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter, sleep


def read_many(read, paths, workers=2):
    if not isinstance(paths, list) or not 1 <= len(paths) <= 4:
        raise ValueError("provide 1..4 paths")
    if len(set(paths)) != len(paths):
        raise ValueError("paths must be distinct")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(read, paths))


def benchmark(read, paths):
    # Explicit injected I/O latency makes the scheduling effect visible on tiny files.
    def delayed(path):
        sleep(0.04)
        return read(path)
    start = perf_counter()
    serial = read_many(delayed, paths, workers=1)
    serial_seconds = perf_counter() - start
    start = perf_counter()
    parallel = read_many(delayed, paths, workers=2)
    return {"same_results": serial == parallel, "serial_seconds": serial_seconds,
            "parallel_seconds": perf_counter() - start, "injected_delay_seconds": 0.04,
            "note": "线程并发读取，不是多 Agent；耗时不作为通过阈值。"}
