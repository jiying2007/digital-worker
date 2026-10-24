#!/usr/bin/env python3
"""Audit live GitHub repository governance against the local stage-aware contract."""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / ".github" / "repository-governance-contract.json"


def api(url: str, token: str | None):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "digital-worker-governance-audit",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def api_list(url: str, token: str | None) -> list:
    items = []
    for page in range(1, 101):
        batch = api(f"{url}?per_page=100&page={page}", token)
        if not isinstance(batch, list):
            raise ValueError("governance API did not return a list")
        items.extend(batch)
        if len(batch) < 100:
            return items
    raise ValueError("governance API pagination exceeds bounded audit limit")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "jiying2007/digital-worker"))
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="enforce the productionization server-governance target even when the current stage is advisory",
    )
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    required = contract["required"]
    stage_policy = contract.get("stage_policy", {})
    current_stage = contract.get("current_stage", "unknown")
    stage_requires_protection = bool(stage_policy.get("server_side_protection_required", True))
    enforcement_required = args.strict or stage_requires_protection

    base = f"https://api.github.com/repos/{args.repository}"
    result = {
        "schema_version": 2,
        "repository": args.repository,
        "contract_status": contract["status"],
        "current_stage": current_stage,
        "enforcement_mode": "strict" if enforcement_required else "advisory",
        "checks": {},
        "status": "BLOCKED",
    }

    try:
        branch_name = urllib.parse.quote(contract["default_branch"], safe="")
        branch = api(f"{base}/branches/{branch_name}", token)
        rulesets = api_list(f"{base}/rulesets", token)
        # GitHub resolves includes, exclusions, target and organization rules.
        # This endpoint only returns active rules applying to this exact branch.
        effective_rules = api_list(f"{base}/rules/branches/{branch_name}", token)
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
            active_details.append(
                {
                    "id": item["id"],
                    "name": item.get("name"),
                    "rule_types": sorted(x for x in rule_types if x),
                    "status_contexts": sorted(status_contexts),
                }
            )

        result["active_rulesets"] = active_details
        required_checks = set(required["required_status_checks"])
        effective_types = {rule.get("type") for rule in effective_rules}
        effective_checks = {
            check["context"]
            for rule in effective_rules if rule.get("type") == "required_status_checks"
            for check in rule.get("parameters", {}).get("required_status_checks", []) if check.get("context")
        }
        result["effective_branch_rule_types"] = sorted(x for x in effective_types if x)
        result["effective_branch_status_contexts"] = sorted(effective_checks)
        ruleset_pass = (result["checks"]["branch_protected"] and
                       {"pull_request", "non_fast_forward", "deletion"} <= effective_types and
                       required_checks <= effective_checks)
        result["checks"]["active_ruleset_contract_pass"] = ruleset_pass

        if ruleset_pass:
            result["status"] = "PASS"
        elif enforcement_required:
            result["status"] = "BLOCKED_SERVER_GOVERNANCE"
        else:
            result["status"] = "DEFERRED_CURRENT_STAGE"
            result["note"] = (
                "Server-side main protection is intentionally advisory during iterative development; "
                "run with --strict before productionization."
            )
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
        result["error"] = str(exc)
        if enforcement_required:
            result["status"] = "BLOCKED_GOVERNANCE_API"
        else:
            result["status"] = "DEFERRED_GOVERNANCE_API_CURRENT_STAGE"

    print(json.dumps(result, ensure_ascii=False, indent=2))

    accepted = {"PASS", "DEFERRED_CURRENT_STAGE", "DEFERRED_GOVERNANCE_API_CURRENT_STAGE"}
    if result["status"] not in accepted and not args.report_only:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
