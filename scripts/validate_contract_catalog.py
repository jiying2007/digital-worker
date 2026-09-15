#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "contracts" / "catalog.json"
REQUIRED = {"id", "version", "path", "owner", "authority", "producer", "consumers", "status", "compatibility"}


def main() -> None:
    doc = json.loads(CATALOG.read_text(encoding="utf-8"))
    assert doc["schema_version"] == 1
    ids = set()
    paths = set()
    for item in doc["contracts"]:
        missing = REQUIRED - set(item)
        assert not missing, f"contract catalog item missing fields: {item.get('id')}: {sorted(missing)}"
        assert item["id"] not in ids, f"duplicate contract id: {item['id']}"
        assert item["path"] not in paths, f"duplicate contract path: {item['path']}"
        ids.add(item["id"]); paths.add(item["path"])
        path = ROOT / item["path"]
        assert path.is_file(), f"catalog path missing: {item['path']}"
        assert item["owner"] == "digital-worker", f"external contract must not be mirrored into local catalog: {item['id']}"
    assert {
        "cross-repo-lock",
        "pilot-evidence-bundle",
        "engineering-task-package",
        "knowledge-reuse-evidence",
        "assurance-provider-evidence",
    } <= ids
    print(f"contract catalog validation PASS: {len(ids)} authoritative local contracts")


if __name__ == "__main__":
    main()
