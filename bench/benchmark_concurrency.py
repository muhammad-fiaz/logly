"""Concurrent logging benchmark for stdlib vs logly v0.1.1.

This script spawns multiple threads and logs to a file to compare throughput.
Tests performance improvements:
- parking_lot RwLock for better multi-threaded performance
- crossbeam-channel for async writes (6x faster)
- Arc<Mutex<>> for thread-safe file writers

Usage (PowerShell):
  python .\bench\benchmark_concurrency.py --threads 4 --count-per-thread 25000 --repeat 2
  python .\bench\benchmark_concurrency.py --threads 8 --count-per-thread 10000 --repeat 3

Options:
  --json          Enable JSON mode for logly
  --pretty-json   Pretty-print JSON for logly (slower, for readability)
  --sync          Force sync writes for logly (default is async)
"""

from __future__ import annotations

import argparse
import logging
import os
import tempfile
import threading
import time
from statistics import mean


def bench_std_concurrent(threads: int, count_per_thread: int) -> float:
    # Single logger with one file handler shared by all threads
    logger = logging.getLogger("std_concurrent")
    logger.setLevel(logging.INFO)
    logger.handlers[:] = []
    logger.propagate = False
    path = os.path.join(tempfile.gettempdir(), "bench_std_concurrent.log")
    fh = logging.FileHandler(path)
    fh.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
    logger.addHandler(fh)

    def worker():  # type: ignore[no-untyped-def]
        for i in range(count_per_thread):
            logger.info("hello %d", i)

    start = time.perf_counter()
    ts = [threading.Thread(target=worker) for _ in range(threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    end = time.perf_counter()

    try:
        fh.flush()
    except Exception:
        pass
    return end - start


def bench_logly_concurrent(
    threads: int, count_per_thread: int, *, json: bool, pretty_json: bool, async_write: bool
) -> float:
    import importlib
    import os as _os
    import sys as _sys

    if _os.getcwd() not in _sys.path:
        _sys.path.insert(0, _os.getcwd())
    import logly  # type: ignore

    importlib.reload(logly)

    # Configure one file sink shared by all threads
    tmp = os.path.join(tempfile.gettempdir(), "bench_logly_concurrent.log")
    # route INFO to file while muting console overhead during the benchmark
    logly.logger.add(tmp, async_write=async_write, filter_min_level="INFO")
    logly.logger.configure(level="ERROR", color=False, json=json, pretty_json=pretty_json)

    def worker():  # type: ignore[no-untyped-def]
        for i in range(count_per_thread):
            logly.logger.info("hello %d", i)

    start = time.perf_counter()
    ts = [threading.Thread(target=worker) for _ in range(threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    # ensure any background writer flushes
    logly.logger.complete()
    end = time.perf_counter()
    return end - start


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--threads", type=int, default=4, help="number of worker threads")
    p.add_argument("--count-per-thread", type=int, default=10000, help="messages each thread emits")
    p.add_argument("--repeat", type=int, default=2, help="repeat runs and average")
    p.add_argument("--json", action="store_true", help="enable JSON mode for logly")
    p.add_argument("--pretty-json", action="store_true", help="pretty-print JSON for logly")
    p.add_argument("--sync", action="store_true", help="force sync writes for logly")
    args = p.parse_args()

    std_runs: list[float] = []
    logly_runs: list[float] = []
    logging.basicConfig(level=logging.INFO)
    logging.info(
        "Concurrent benchmark: threads=%d, count_per_thread=%d, repeat=%d",
        args.threads,
        args.count_per_thread,
        args.repeat,
    )

    for _ in range(args.repeat):
        t = bench_std_concurrent(args.threads, args.count_per_thread)
        logging.info("std concurrent run: %.4fs", t)
        std_runs.append(t)

    for _ in range(args.repeat):
        t = bench_logly_concurrent(
            args.threads,
            args.count_per_thread,
            json=args.json,
            pretty_json=args.pretty_json,
            async_write=not args.sync,
        )
        logging.info("logly concurrent run: %.4fs", t)
        logly_runs.append(t)

    logging.info("\nSummary (seconds):")
    logging.info("std   mean: %.4f  runs: %s", mean(std_runs), std_runs)
    logging.info(
        "logly mean: %.4f  runs: %s  (json=%s, pretty=%s, async=%s)",
        mean(logly_runs),
        logly_runs,
        args.json,
        args.pretty_json,
        not args.sync,
    )


if __name__ == "__main__":
    main()
