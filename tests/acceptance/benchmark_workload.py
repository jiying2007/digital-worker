"""Isolated acceptance workload, run against either exact source snapshot."""
from __future__ import annotations

import hashlib
import json
import math
import platform
import shutil
import statistics
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path


def main():
    source = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(source / "scripts"))
    sys.path.insert(0, str(source / "tests/unit"))
    import embedded_pilot as pilot
    import evaluate_edge_foundation_pilot as receipt_tool
    import evaluate_edge_foundation_product_readiness as readiness
    import test_review_hardening as fixtures
    with tempfile.TemporaryDirectory() as tmp:
        root = fixtures.fixture_run(Path(tmp) / "run")
        receipt_path = root / "edge-foundation-pilot-receipt.json"
        fixtures.write(receipt_path, fixtures.generate(root))
        workloads = {
            "validate": lambda: pilot.validate_run_dir(root),
            "receipt": lambda: receipt_tool.build_receipt(root / "pilot-run.json", root / "pilot_result.json", None),
            "readiness": lambda: readiness.evaluate([receipt_path]),
        }
        result = {"python": platform.python_version(), "platform": platform.system(), "warmups": 3, "samples": 20, "operations": {}}
        for name, operation in workloads.items():
            for _ in range(3): operation()
            samples = []
            for _ in range(20):
                start = time.perf_counter()
                operation()
                samples.append((time.perf_counter() - start) * 1000)
            result["operations"][name] = {"median_ms": statistics.median(samples),
                                           "p95_ms": sorted(samples)[math.ceil(.95 * len(samples)) - 1],
                                           "samples_ms": samples}
        # Batch validation is not a distinct-run cohort qualification claim.
        batch = Path(tmp) / "batch"
        batch.mkdir()
        for index in range(100): shutil.copytree(root, batch / str(index))
        start = time.perf_counter()
        for item in sorted(batch.iterdir()): pilot.validate_run_dir(item)
        result["batch_100_independent_layouts_ms"] = (time.perf_counter() - start) * 1000
        artifact = Path(tmp) / "large-artifact"
        chunk = b"x" * (1024 * 1024)
        with artifact.open("wb") as stream:
            for _ in range(32): stream.write(chunk)
        tracemalloc.start()
        digest = pilot.sha256(artifact)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        expected = hashlib.sha256()
        for _ in range(32): expected.update(chunk)
        assert digest == expected.hexdigest()
        assert peak < 4 * 1024 * 1024, peak
        result["stream_hash"] = {"artifact_bytes": artifact.stat().st_size, "peak_python_bytes": peak, "digest_correct": True}
        print(json.dumps(result))


if __name__ == "__main__":
    main()
