#!/usr/bin/env python3
"""Compatibility entrypoint for human-view validation.

The old overview/position validator duplicated the legacy organization model. Human
view validation is now owned by validate_core_reference.py so there is one target-
first rule set and no second organizational SSOT.
"""
from __future__ import annotations

from validate_core_reference import main


if __name__ == "__main__":
    main()
