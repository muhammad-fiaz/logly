"""Simple benchmark comparing Python stdlib logging vs logly v0.1.1.

Usage examples (PowerShell):

# Quick run comparing console logging:
python .\bench\benchmark_logging.py --mode console --count 10000 --repeat 3

# Compare file logging (writes to temp files):
python .\bench\benchmark_logging.py --mode file --count 20000 --repeat 3

# Large-scale benchmark (100k logs):
python .\bench\benchmark_logging.py --mode file --count 100000 --repeat 5

The script times how long it takes to emit N log records for each backend.
Tests performance improvements in logly v0.1.1:
- parking_lot RwLock (5-10x faster)
- crossbeam-channel async (6x faster async writes)
- ahash HashMap (30% faster hashing)
- Arc<Mutex<>> thread-safe writers
"""

from __future__ import annotations

import argparse
import logging
import os
import tempfile
import time
from statistics import mean


def bench_std_logging(
    count: int,
    to_file: bool,
    *,
    message_size: int = 0,
    fields: int = 0,
    level_mix: bool = False,
    output_path: str | None = None,
) -> float:
    logger = logging.getLogger("std_logger")
    logger.setLevel(logging.INFO)
    # remove handlers
    logger.handlers[:] = []
    # prevent propagation to root logger to avoid console output during file benchmarks
    logger.propagate = False
    # If output_path is provided, write to that file even in "console" mode
    if to_file or output_path:
        path = output_path if output_path else os.path.join(tempfile.gettempdir(), "bench_std.log")
        fh = logging.FileHandler(path)
        fmt = logging.Formatter("%(levelname)s:%(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    else:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
        logger.addHandler(ch)

    # Prepare a base message and optional payload fields
    base = "hello {}" + (" " + ("x" * message_size) if message_size > 0 else "")
    payload_suffix = ""
    if fields > 0:
        payload_suffix = "".join([f" k{j}={j}" for j in range(fields)])

    start = time.perf_counter()
    for i in range(count):
        if level_mix and (i % 10 == 0):
            logger.debug(base.format(i) + payload_suffix)  # lower volume DEBUG
            continue
        logger.info(base.format(i) + payload_suffix)
    end = time.perf_counter()
    # flush file handlers
    for h in logger.handlers:
        try:
            h.flush()
        except Exception:
            pass
    return end - start


def bench_logly(
    count: int,
    to_file: bool,
    *,
    json: bool = False,
    pretty_json: bool = False,
    async_write: bool = True,
    message_size: int = 0,
    fields: int = 0,
    level_mix: bool = False,
    output_path: str | None = None,
) -> float:
    # ensure local project package is preferred when running from repo root
    import importlib
    import sys

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

    # Add sinks fairly: console only for console mode; file-only for file mode
    # Support "console" mode that writes to a temp file (output_path) so the terminal
    # doesn't affect timing, while preserving the same formatting costs.
    if to_file:
        tmp = os.path.join(tempfile.gettempdir(), "bench_logly.log")
        # add file sink before configure() per MVP; allow INFO to file while muting console with global level
        logly.logger.add(tmp, async_write=async_write, filter_min_level="INFO")
        # Mute console to avoid stderr overhead in file benchmark by using a higher global level
        logly.logger.configure(level="ERROR", color=False, json=json, pretty_json=pretty_json)
    else:
        if output_path:
            tmp = output_path
            # write console-formatted output into a file to avoid terminal overhead
            logly.logger.add(tmp, async_write=async_write, filter_min_level="INFO")
            logly.logger.configure(level="ERROR", color=False, json=json, pretty_json=pretty_json)
        else:
            logly.logger.add("console")
            logly.logger.configure(level="INFO", color=False, json=json, pretty_json=pretty_json)

    # Prepare base message and a synthetic payload dict
    base = "hello {}" + (" " + ("x" * message_size) if message_size > 0 else "")
    payload: dict[str, int] = {f"k{j}": j for j in range(fields)} if fields > 0 else {}

    start = time.perf_counter()
    for i in range(count):
        if level_mix and (i % 10 == 0):
            logly.logger.debug(base.format(i), **payload)
            continue
        logly.logger.info(base.format(i), **payload)
    # ensure flush
    logly.logger.complete()
    end = time.perf_counter()
    return end - start


def main():  # type: ignore[no-untyped-def]
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=10000, help="number of log messages per run")
    p.add_argument("--repeat", type=int, default=3, help="how many times to repeat and average")
    p.add_argument("--mode", choices=("console", "file"), default="console")
    p.add_argument("--json", action="store_true", help="enable JSON mode for logly runs")
    p.add_argument("--pretty-json", action="store_true", help="pretty-print JSON (higher cost)")
    p.add_argument("--sync", action="store_true", help="force sync file writes (async by default)")
    p.add_argument(
        "--message-size",
        type=int,
        default=0,
        help="extra message size in bytes to append to each line",
    )
    p.add_argument(
        "--fields", type=int, default=0, help="number of synthetic key=value fields per call"
    )
    p.add_argument(
        "--level-mix", action="store_true", help="mix in DEBUG logs (10%) alongside INFO"
    )
    args = p.parse_args()

    to_file = args.mode == "file"

    std_results = []
    logly_results = []
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Benchmarking {args.count} messages, mode={args.mode}, repeat={args.repeat}")

    # When running in console mode, write the formatted output to a temp file so
    # terminal I/O doesn't skew timings; in file mode we keep the normal file path.
    output_path = None
    if args.mode == "console":
        output_path = os.path.join(tempfile.gettempdir(), "bench_console_out.txt")

    for _ in range(args.repeat):
        t = bench_std_logging(
            args.count,
            to_file,
            message_size=args.message_size,
            fields=args.fields,
            level_mix=args.level_mix,
            output_path=output_path,
        )
        logging.info(f"std logging run: {t:.4f}s")
        std_results.append(t)

    for _ in range(args.repeat):
        t = bench_logly(
            args.count,
            to_file,
            json=args.json,
            pretty_json=args.pretty_json,
            async_write=not args.sync,
            message_size=args.message_size,
            fields=args.fields,
            level_mix=args.level_mix,
            output_path=output_path,
        )
        logging.info(f"logly run: {t:.4f}s")
        logly_results.append(t)

    logging.info("\nSummary (seconds):")
    logging.info(f"std   mean: {mean(std_results):.4f}  runs: {std_results}")
    logging.info(
        f"logly mean: {mean(logly_results):.4f}  runs: {logly_results}  "
        f"(json={args.json}, pretty={args.pretty_json}, async={not args.sync}, mode={args.mode}, msg_size={args.message_size}, fields={args.fields}, level_mix={args.level_mix})"
    )


if __name__ == "__main__":
    main()
