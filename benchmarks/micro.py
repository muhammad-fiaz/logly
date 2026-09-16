"""Micro-benchmarks for the Logly hot path (stdlib only).

Usage:
    python benchmarks/micro.py [--iterations N]

Reports median nanoseconds per log call for disabled, console, file,
formatted, JSON, lazy, bound-context, and enqueue logging.
"""

from __future__ import annotations

import io
import statistics
import sys
import tempfile
import time
from pathlib import Path


def _bench(label: str, iterations: int, func) -> None:
    func()  # warmup
    samples: list[float] = []
    batch = max(1, iterations // 20)
    for _ in range(20):
        start = time.perf_counter_ns()
        for _ in range(batch):
            func()
        samples.append((time.perf_counter_ns() - start) / batch)
    print(f"{label:28s} {statistics.median(samples):12.1f} ns/call")


def main() -> None:
    iterations = (
        int(sys.argv[sys.argv.index("--iterations") + 1]) if "--iterations" in sys.argv else 2000
    )

    from logly import Logger

    quiet = Logger()
    quiet.disable("logly")
    _bench("disabled logger", iterations, lambda: quiet.info("hidden {}", 1))

    plain = Logger()
    plain.add(io.StringIO(), format="{message}")
    _bench("console callback", iterations, lambda: plain.info("hello {}", "world"))

    formatted = Logger()
    formatted.add(io.StringIO())
    _bench("default format", iterations, lambda: formatted.info("hello {}", "world"))

    json_log = Logger()
    json_log.add(io.StringIO(), serialize=True)
    _bench("json serialize", iterations, lambda: json_log.info("hello {}", "world"))

    lazy = Logger()
    lazy.add(io.StringIO(), format="{message}")
    _bench("lazy argument", iterations, lambda: lazy.opt(lazy=True).info("v=[{}]", lambda: "x"))

    bound = Logger().bind(user="alice", request="r1")
    bound.add(io.StringIO(), format="{message}")
    _bench("bound context", iterations, lambda: bound.info("hello"))

    tmp = Path(tempfile.mkdtemp()) / "bench.log"
    file_log = Logger()
    file_log.add(str(tmp), format="{message}")
    _bench("file sink", iterations, lambda: file_log.info("hello {}", "world"))
    file_log.complete()
    file_log.remove()

    dropped = 0

    def enqueue_one() -> None:
        nonlocal dropped
        try:
            queued.info("hello")
        except RuntimeError:
            # Bounded queue with drop-newest backpressure reports drops.
            dropped += 1

    queued = Logger()
    queued.add(io.StringIO(), format="{message}", enqueue=True)
    _bench("enqueue sink", iterations, enqueue_one)
    queued.complete()
    queued.remove()
    if dropped:
        print(f"(enqueue drops under load: {dropped})")

    print("done")


if __name__ == "__main__":
    main()
