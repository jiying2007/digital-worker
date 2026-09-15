#!/usr/bin/env python3
"""Fail if active repository surfaces still depend on the retired embedded legacy tree."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_PATH = "expert-groups" + "/embedded-system"

SCAN_ROOTS = [
    ROOT / "README.md",
    ROOT / ".github" / "workflows",
    ROOT / "scripts",
    ROOT / "domains" / "edge-foundation",
    ROOT / "tests",
    ROOT / "docs" / "runbooks",
    ROOT / "docs" / "strategy",
    ROOT / "嵌入式系统专家团-核心参考",
]
SUFFIXES = {".py", ".yml", ".yaml", ".json", ".md", ".toml", ".txt"}
SELF = Path(__file__).resolve()


def iter_files(root: Path):
    if root.is_file():
        yield root
        return
    if not root.exists():
        return
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUFFIXES:
            yield path


def main() -> None:
    refs: list[str] = []
    for root in SCAN_ROOTS:
        for path in iter_files(root):
            if path.resolve() == SELF:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for lineno, line in enumerate(text.splitlines(), 1):
                if LEGACY_PATH in line:
                    refs.append(f"{path.relative_to(ROOT)}:{lineno}: {line.strip()}")
    if refs:
        print("active live references to retired legacy tree detected:")
        for item in refs:
            print(f"- {item}")
        raise SystemExit(2)
    print("zero-live-legacy-reference PASS")


if __name__ == "__main__":
    main()
