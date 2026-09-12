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

# Automated execution is limited to reviewed changes on main that modify the GC workflow or its allowlist.
if "branches: [main]" not in text:
    fail("Branch GC push trigger must stay limited to main")
for trigger_path in ["'.github/workflows/branch-gc.yml'", "'.github/branch-gc-allowlist.txt'"]:
    if trigger_path not in text:
        fail(f"Branch GC audited push trigger missing: {trigger_path}")

branches = []
for raw in allowlist.read_text(encoding="utf-8").splitlines():
    line = raw.split("#", 1)[0].strip()
    if line:
        branches.append(line)

if not branches:
    fail("Branch GC allowlist must contain at least one reviewed branch")
if "main" in branches:
    fail("main must never appear in Branch GC allowlist")
if len(branches) != len(set(branches)):
    fail("Branch GC allowlist contains duplicate entries")

# All entries are still explicit/reviewed allowlist items and remain subject to
# main/protected/open-PR/merged-PR guards in the workflow. `arch/` is a normal
# temporary architecture task class, equivalent in lifecycle to `design/`.
allowed_prefixes = ("docs/", "feat/", "fix/", "refactor/", "design/", "arch/", "chore/", "research/", "release/")
for branch in branches:
    if not branch.startswith(allowed_prefixes):
        fail(f"unexpected branch class in GC allowlist: {branch}")

print(f"Branch GC safety contract OK ({len(branches)} approved branch(es))")
