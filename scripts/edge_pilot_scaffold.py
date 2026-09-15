#!/usr/bin/env python3
"""Edge Foundation scaffold using target schemas."""
from pathlib import Path
import embedded_pilot_scaffold as impl

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
impl.MATERIAL_SCHEMA = EDGE / "schemas" / "material-manifest.schema.json"
impl.HYPOTHESIS_SCHEMA = EDGE / "schemas" / "hypothesis-registry.schema.json"

if __name__ == "__main__":
    impl.main()
