#!/usr/bin/env python3
"""Validate Material Manifest against Edge Foundation target schema."""
from pathlib import Path
import validate_material_manifest as impl

ROOT = Path(__file__).resolve().parents[1]
impl.SCHEMA = ROOT / "domains" / "edge-foundation" / "schemas" / "material-manifest.schema.json"

if __name__ == "__main__":
    impl.main()
