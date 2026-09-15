#!/usr/bin/env python3
"""Evaluate Pilot results using Edge Foundation target Pilot plan."""
from pathlib import Path
import evaluate_embedded_pilot as impl

ROOT = Path(__file__).resolve().parents[1]
impl.DEFAULT_PLAN = ROOT / "domains" / "edge-foundation" / "pilot" / "pilot-plan.yaml"

if __name__ == "__main__":
    impl.main()
