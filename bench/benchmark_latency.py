"""Latency microbenchmark for stdlib logging vs logly.

Measures p50/p95/p99 latency for console or file sinks.

Usage (PowerShell):
  python .\bench\benchmark_latency.py --mode console --count 20000
  python .\bench\benchmark_latency.py --mode file --json --count 30000
"""

from __future__ import annotations

import argparse
import logging
import os
import tempfile
import time
from collections.abc import Iterable


def percentiles(values: Iterable[float], ps: list[float]) -> list[float]:
    xs = sorted(values)
    n = len(xs)
    out: list[float] = []
    for p in ps:
        if n == 0:
            out.append(float("nan"))
            continue
        k = (n - 1) * p
        f = int(k)
        c = min(f + 1, n - 1)
        if f == c:
            out.append(xs[int(k)])
        else:
            d0 = xs[f] * (c - k)
            d1 = xs[c] * (k - f)
            out.append(d0 + d1)
    return out


def bench_std_latency(count: int, to_file: bool) -> list[float]:
    logger = logging.getLogger("std_latency")
    logger.setLevel(logging.INFO)
    logger.handlers[:] = []
    logger.propagate = False
    if to_file:
        fh = logging.FileHandler(os.path.join(tempfile.gettempdir(), "bench_std_latency.log"))
        fh.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
        logger.addHandler(fh)
    else:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
        logger.addHandler(ch)

    latencies: list[float] = []
    for i in range(count):
        t0 = time.perf_counter_ns()
        logger.info("hello %d", i)
        t1 = time.perf_counter_ns()
        latencies.append((t1 - t0) / 1e6)  # ms
    for h in logger.handlers:
        try:
            h.flush()
        except Exception:
            pass
    return latencies


essential_import_done = False


def bench_logly_latency(
    count: int, to_file: bool, *, json: bool, pretty_json: bool, async_write: bool
) -> list[float]:
    import importlib
    import sys

    global essential_import_done
    if not essential_import_done:
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())
        essential_import_done = True

    import logly  # type: ignore

    importlib.reload(logly)

    if to_file:
        tmp = os.path.join(tempfile.gettempdir(), "bench_logly_latency.log")
        logly.logger.add(tmp, async_write=async_write, filter_min_level="INFO")
        logly.logger.configure(level="ERROR", color=False, json=json, pretty_json=pretty_json)
    else:
        logly.logger.add("console")
        logly.logger.configure(level="INFO", color=False, json=json, pretty_json=pretty_json)

    latencies: list[float] = []
    for i in range(count):
        t0 = time.perf_counter_ns()
        logly.logger.info("hello %d", i)
        t1 = time.perf_counter_ns()
        latencies.append((t1 - t0) / 1e6)
    logly.logger.complete()
    return latencies


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=20000)
    p.add_argument("--mode", choices=("console", "file"), default="console")
    p.add_argument("--json", action="store_true")
    p.add_argument("--pretty-json", action="store_true")
    p.add_argument("--sync", action="store_true")
    args = p.parse_args()

    to_file = args.mode == "file"

    logging.basicConfig(level=logging.INFO)
    logging.info("Latency benchmark: mode=%s, count=%d", args.mode, args.count)

    std_lat = bench_std_latency(args.count, to_file)
    logly_lat = bench_logly_latency(
        args.count, to_file, json=args.json, pretty_json=args.pretty_json, async_write=not args.sync
    )

    std_p50, std_p95, std_p99 = percentiles(std_lat, [0.5, 0.95, 0.99])
    logly_p50, logly_p95, logly_p99 = percentiles(logly_lat, [0.5, 0.95, 0.99])

    logging.info("\nLatency (ms):")
    logging.info("std   p50=%.3f  p95=%.3f  p99=%.3f", std_p50, std_p95, std_p99)
    logging.info(
        "logly p50=%.3f  p95=%.3f  p99=%.3f  (json=%s, pretty=%s, async=%s)",
        logly_p50,
        logly_p95,
        logly_p99,
        args.json,
        args.pretty_json,
        not args.sync,
    )


if __name__ == "__main__":
    main()
