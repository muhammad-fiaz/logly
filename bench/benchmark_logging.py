"""Simple benchmark comparing Python stdlib logging vs logly.

Usage examples (PowerShell):

# Quick run comparing console logging:
python .\bench\benchmark_logging.py --mode console --count 10000 --repeat 3

# Compare file logging (writes to temp files):
python .\bench\benchmark_logging.py --mode file --count 20000 --repeat 3

The script times how long it takes to emit N log records for each backend.
"""

from __future__ import annotations

import argparse
import logging
import os
import tempfile
import time
from statistics import mean


def bench_std_logging(count: int, to_file: bool) -> float:
    logger = logging.getLogger("std_logger")
    logger.setLevel(logging.INFO)
    # remove handlers
    logger.handlers[:] = []
    if to_file:
        fh = logging.FileHandler(os.path.join(tempfile.gettempdir(), "bench_std.log"))
        fmt = logging.Formatter("%(levelname)s:%(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    else:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
        logger.addHandler(ch)

    start = time.perf_counter()
    for i in range(count):
        logger.info("hello %d", i)
    end = time.perf_counter()
    # flush file handlers
    for h in logger.handlers:
        try:
            h.flush()
        except Exception:
            pass
    return end - start


def bench_logly(count: int, to_file: bool) -> float:
    # ensure local project package is preferred when running from repo root
    import sys
    import importlib

    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())

    # import inside function so the module import cost is not measured
    import logly

    importlib.reload(logly)

    # ensure fresh configuration
    # remove previous sinks is a no-op in MVP, but we call add
    # ensure logger exists (extension must be built via maturin develop or package installed)
    if not hasattr(logly, "logger"):
        raise RuntimeError(
            "logly package does not expose 'logger'. Build the extension with 'maturin develop' or install the package before running the benchmark."
        )

    # add console sink (no-op if already present)
    logly.logger.add("console")
    if to_file:
        tmp = os.path.join(tempfile.gettempdir(), "bench_logly.log")
        # add file sink before configure() per MVP
        logly.logger.add(tmp)
    logly.logger.configure(level="INFO", color=False)

    start = time.perf_counter()
    for i in range(count):
        logly.logger.info("hello %d", i)
    # ensure flush
    logly.logger.complete()
    end = time.perf_counter()
    return end - start


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=10000, help="number of log messages per run")
    p.add_argument("--repeat", type=int, default=3, help="how many times to repeat and average")
    p.add_argument("--mode", choices=("console", "file"), default="console")
    args = p.parse_args()

    to_file = args.mode == "file"

    std_results = []
    logly_results = []
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Benchmarking {args.count} messages, mode={args.mode}, repeat={args.repeat}")

    for _ in range(args.repeat):
        t = bench_std_logging(args.count, to_file)
        logging.info(f"std logging run: {t:.4f}s")
        std_results.append(t)

    for _ in range(args.repeat):
        t = bench_logly(args.count, to_file)
        logging.info(f"logly run: {t:.4f}s")
        logly_results.append(t)

    logging.info("\nSummary (seconds):")
    logging.info(f"std   mean: {mean(std_results):.4f}  runs: {std_results}")
    logging.info(f"logly mean: {mean(logly_results):.4f}  runs: {logly_results}")


if __name__ == "__main__":
    main()
