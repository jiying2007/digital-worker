#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
workflow = ROOT / ".github/workflows/branch-gc.yml"
allowlist = ROOT / ".github/branch-gc-allowlist.txt"

def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)

for path in (workflow, allowlist):
    if not path.is_file():
        fail(f"missing required Branch GC asset: {path.relative_to(ROOT)}")

text = workflow.read_text(encoding="utf-8")
required_snippets = [
    "workflow_dispatch:",
    "contents: write",
    "pull-requests: read",
    "refusing to delete main",
    "protected branch; refusing GC",
    "open PR(s); refusing GC",
    "no merged PR evidence; refusing GC",
    ".github/branch-gc-allowlist.txt",
    "--method DELETE",
    "git/refs/heads/",
    "dry-run PASS; would delete",
]
for snippet in required_snippets:
    if snippet not in text:
        fail(f"Branch GC safety contract missing: {snippet!r}")

# Bootstrap execution is intentionally limited to first/update merge of the GC workflow itself.
if "branches: [main]" not in text or "'.github/workflows/branch-gc.yml'" not in text:
    fail("bootstrap push trigger must be limited to main + branch-gc.yml path")

branches = []
for raw in allowlist.read_text(encoding="utf-8").splitlines():
    line = raw.split("#", 1)[0].strip()
    if line:
        branches.append(line)

if not branches:
    fail("Branch GC allowlist must not be empty during bootstrap rollout")
if "main" in branches:
    fail("main must never appear in Branch GC allowlist")
if len(branches) != len(set(branches)):
    fail("Branch GC allowlist contains duplicate entries")

allowed_prefixes = ("docs/", "feat/", "fix/", "refactor/", "design/", "chore/", "research/", "release/")
for branch in branches:
    if not branch.startswith(allowed_prefixes):
        fail(f"unexpected branch class in GC allowlist: {branch}")

print(f"Branch GC safety contract OK ({len(branches)} approved branch(es))")
