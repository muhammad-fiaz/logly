"""Benchmark matrix runner for logly vs stdlib.

Runs a small matrix of scenarios:
- mode: console | file
- json: off/on
- pretty_json: off/on (only when json on)
- async: on/off (file mode only)

Usage (PowerShell):
python .\bench\benchmark_matrix.py --count 50000 --repeat 2
"""
from __future__ import annotations

import argparse
import logging
import subprocess
import sys


def run(cmd: list[str]) -> None:
    logging.info("$ %s", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=20000)
    p.add_argument("--repeat", type=int, default=2)
    args = p.parse_args()

    py = sys.executable
    base = [py, "-m", "pip", "--version"]  # sanity
    subprocess.run(base, check=True, stdout=subprocess.DEVNULL)

    scenarios: list[list[str]] = []
    # console, text
    scenarios.append([py, "bench/benchmark_logging.py", "--mode", "console", "--count", str(args.count), "--repeat", str(args.repeat)])
    # file, text, async
    scenarios.append([py, "bench/benchmark_logging.py", "--mode", "file", "--count", str(args.count), "--repeat", str(args.repeat)])
    # file, text, sync
    scenarios.append([py, "bench/benchmark_logging.py", "--mode", "file", "--sync", "--count", str(args.count), "--repeat", str(args.repeat)])
    # console, json compact
    scenarios.append([py, "bench/benchmark_logging.py", "--mode", "console", "--json", "--count", str(args.count), "--repeat", str(args.repeat)])
    # file, json compact, async
    scenarios.append([py, "bench/benchmark_logging.py", "--mode", "file", "--json", "--count", str(args.count), "--repeat", str(args.repeat)])
    # file, json compact, sync
    scenarios.append([py, "bench/benchmark_logging.py", "--mode", "file", "--json", "--sync", "--count", str(args.count), "--repeat", str(args.repeat)])
    # console, json pretty
    scenarios.append([py, "bench/benchmark_logging.py", "--mode", "console", "--json", "--pretty-json", "--count", str(args.count), "--repeat", str(args.repeat)])

    logging.basicConfig(level=logging.INFO)
    for cmd in scenarios:
        run(cmd)


if __name__ == "__main__":
    main()
