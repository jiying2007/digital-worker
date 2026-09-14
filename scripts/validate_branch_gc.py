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
    "current tip has neither exact merged-PR evidence nor main ancestry; refusing GC",
    "headRefOid",
    "exact-merged-pr-head",
    "tip-contained-by-main",
    "compare/${tip_sha}...${GITHUB_SHA}",
    "if ! ref_json=",
    "already absent",
    ".object.sha // empty",
    ".github/branch-gc-allowlist.txt",
    "--method DELETE",
    "git/refs/heads/",
    "dry-run PASS",
    "allowlist is empty; nothing to do",
    "actions/checkout@11d5960a326750d5838078e36cf38b85af677262",
]
for snippet in required_snippets:
    if snippet not in text:
        fail(f"Branch GC safety contract missing: {snippet!r}")

if "branches: [main]" not in text:
    fail("Branch GC push trigger must stay limited to main")
for trigger_path in ["'.github/workflows/branch-gc.yml'", "'.github/branch-gc-allowlist.txt'"]:
    if trigger_path not in text:
        fail(f"Branch GC audited push trigger missing: {trigger_path}")

# A historical merged PR alone is insufficient: evidence must bind to current tip
# or prove that the current tip is already contained by main.
for forbidden in [
    "no merged PR evidence; refusing GC",
    "[.[] | select(.mergedAt != null)] | length",
    'ref_json="$(gh api "repos/${GITHUB_REPOSITORY}/git/ref/heads/${encoded}" 2>/dev/null || true)"',
]:
    if forbidden in text:
        fail(f"Branch GC retained unsafe or ambiguous evidence handling: {forbidden!r}")

branches = []
for raw in allowlist.read_text(encoding="utf-8").splitlines():
    line = raw.split("#", 1)[0].strip()
    if line:
        branches.append(line)

if "main" in branches:
    fail("main must never appear in Branch GC allowlist")
if len(branches) != len(set(branches)):
    fail("Branch GC allowlist contains duplicate entries")

allowed_prefixes = ("docs/", "feat/", "fix/", "refactor/", "design/", "arch/", "chore/", "research/", "release/", "codex/")
for branch in branches:
    if not branch.startswith(allowed_prefixes):
        fail(f"unexpected branch class in GC allowlist: {branch}")

print(f"Branch GC safety contract OK ({len(branches)} pending approved branch(es); current-tip evidence + absent-ref handling required)")
