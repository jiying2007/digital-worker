#!/usr/bin/env python3
"""Audit live GitHub repository governance against the local contract."""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / ".github" / "repository-governance-contract.json"


def api(url: str, token: str | None):
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "digital-worker-governance-audit"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "jiying2007/digital-worker"))
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()
    token = os.environ.get("GITHUB_TOKEN")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    required = contract["required"]
    base = f"https://api.github.com/repos/{args.repository}"
    result = {"schema_version": 1, "repository": args.repository, "contract_status": contract["status"], "checks": {}, "status": "BLOCKED"}
    try:
        branch = api(f"{base}/branches/{contract['default_branch']}", token)
        rulesets = api(f"{base}/rulesets", token)
        result["checks"]["branch_protected"] = bool(branch.get("protected"))
        result["checks"]["ruleset_count"] = len(rulesets)
        active_details = []
        for item in rulesets:
            if item.get("enforcement") != "active":
                continue
            try:
                detail = api(f"{base}/rulesets/{item['id']}", token)
            except urllib.error.HTTPError:
                continue
            rule_types = {rule.get("type") for rule in detail.get("rules", [])}
            status_contexts = set()
            for rule in detail.get("rules", []):
                if rule.get("type") == "required_status_checks":
                    for check in rule.get("parameters", {}).get("required_status_checks", []):
                        if check.get("context"):
                            status_contexts.add(check["context"])
            active_details.append({"id": item["id"], "name": item.get("name"), "rule_types": sorted(x for x in rule_types if x), "status_contexts": sorted(status_contexts)})
        result["active_rulesets"] = active_details
        required_checks = set(required["required_status_checks"])
        ruleset_pass = any(
            "pull_request" in d["rule_types"]
            and "non_fast_forward" in d["rule_types"]
            and "deletion" in d["rule_types"]
            and required_checks.issubset(set(d["status_contexts"]))
            for d in active_details
        )
        result["checks"]["active_ruleset_contract_pass"] = ruleset_pass
        # Legacy protection counts as server enforcement but cannot be accepted as fully
        # audited unless the exact required rules can be read. Prefer repository rulesets.
        result["status"] = "PASS" if ruleset_pass else "BLOCKED_SERVER_GOVERNANCE"
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        result["status"] = "BLOCKED_GOVERNANCE_API"
        result["error"] = str(exc)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS" and not args.report_only:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
