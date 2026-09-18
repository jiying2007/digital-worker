#!/usr/bin/env python3
"""Generate a deterministic reviewer-facing snapshot from canonical repository assets.

This is a derived view only. It must not become a new routing, maturity, Product
Readiness, Runtime Qualification, or Productionization authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
CORE = ROOT / "嵌入式系统专家团-核心参考"
SCHEMA = ROOT / "schemas" / "edge-foundation-review-snapshot.v1.schema.json"

SKILL_REQUIRED_SECTIONS = [
    "## Purpose",
    "## Use When",
    "## Do Not Use For",
    "## Required Inputs",
    "## Optional Inputs",
    "## Method",
    "## Outputs",
    "## Evidence Rules",
    "## BLOCK Conditions",
    "## Verification / Review Handoff",
    "## Evaluation",
    "## Known Limits / Change Notes",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_json(value: dict, schema_path: Path) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def review_grade_skill_count(skills: list[dict]) -> int:
    count = 0
    for item in skills:
        path = EDGE / item["path"]
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if all(section in text for section in SKILL_REQUIRED_SECTIONS):
            count += 1
    return count


def retained_skill_summaries() -> tuple[list[str], int]:
    evidence_root = EDGE / "evaluation" / "evidence"
    if not evidence_root.exists():
        return [], 0
    evaluated: list[str] = []
    total = 0
    for path in sorted(evidence_root.rglob("*.json")):
        try:
            value = load_json(path)
        except Exception:
            continue
        if value.get("schema_version") != 1 or "evaluation_complete" not in value or "skill_id" not in value:
            continue
        try:
            validate_json(value, ROOT / "schemas" / "skill-evaluation-summary.v1.schema.json")
        except Exception:
            continue
        total += 1
        if value["status"] == "EVALUATED" and value["evaluation_complete"] is True:
            evaluated.append(value["skill_id"])
    return sorted(set(evaluated)), total


def retained_real_skill_invocations() -> tuple[list[str], int]:
    evidence_root = EDGE / "pilot" / "evidence"
    if not evidence_root.exists():
        return [], 0
    skill_ids: list[str] = []
    total = 0
    for path in sorted(evidence_root.rglob("*.json")):
        try:
            value = load_json(path)
        except Exception:
            continue
        if not {"skill_id", "skill_contract", "runtime_binding", "attestation", "source_type"} <= set(value):
            continue
        try:
            validate_json(value, ROOT / "schemas" / "skill-invocation-receipt.v1.schema.json")
        except Exception:
            continue
        if value["source_type"] == "real":
            total += 1
            skill_ids.append(value["skill_id"])
    return sorted(set(skill_ids)), total


def retained_real_pilot_results() -> tuple[int, int, dict[str, int]]:
    by_track = {"debug": 0, "feature": 0, "review_release": 0}
    total = 0
    passed = 0
    evidence_root = EDGE / "pilot" / "evidence"
    if not evidence_root.exists():
        return total, passed, by_track
    for path in sorted(evidence_root.rglob("pilot-result.json")):
        value = load_json(path)
        validate_json(value, ROOT / "schemas" / "pilot-result.v1.schema.json")
        if value["source_type"] != "real":
            continue
        total += 1
        if value["outcome"] == "PASS":
            passed += 1
            by_track[value["pilot_track"]] += 1
    return total, passed, by_track


def runtime_r2_state() -> tuple[int, int, str]:
    freeze_root = ROOT / "reports" / "runtime-r2" / "freeze"
    receipts = sorted(freeze_root.rglob("freeze-receipt.json")) if freeze_root.exists() else []
    qualified = 0
    for path in receipts:
        value = load_json(path)
        if value.get("authority_boundary", {}).get("r2_qualified") is True:
            qualified += 1
    if qualified:
        status = "QUALIFIED_EVIDENCE_PRESENT"
    elif receipts:
        status = "FROZEN_PENDING_QUALIFICATION"
    else:
        status = "NO_RETAINED_EVIDENCE"
    return len(receipts), qualified, status


def build_snapshot() -> dict:
    domain = load_yaml(EDGE / "domain.yaml")
    routing = load_yaml(EDGE / "routing.yaml")
    gates = load_yaml(EDGE / "gate-policy.yaml")
    registry = load_yaml(EDGE / "skills.yaml")
    eval_plan = load_yaml(EDGE / "evaluation" / "skill-evaluation-plan.yaml")
    skills = registry["skills"]

    embedded = next(item for item in domain["experts"] if item["id"] == "embedded-system-expert")
    positive = sum(1 for cases in eval_plan["skills"].values() if "positive" in cases)
    block = sum(1 for cases in eval_plan["skills"].values() if "block" in cases)

    evaluated_ids, retained_summaries = retained_skill_summaries()
    real_skill_ids, real_invocations = retained_real_skill_invocations()
    pilot_total, pilot_pass, pilot_by_track = retained_real_pilot_results()
    r2_freeze, r2_qualified, r2_status = runtime_r2_state()

    review_files = {
        "root_skills_index": ROOT / "SKILLS.md",
        "review_guide": CORE / "00-评审导览" / "01 评审总览与阅读路径.md",
        "maturity_ledger": CORE / "05-工程交付" / "06 Skill评审成熟度台账.md",
        "evaluation_guide": CORE / "05-工程交付" / "07 Skill评测与证据闭环.md",
        "end_to_end_checklist": CORE / "06-治理与评审" / "07 端到端评审检查表.md",
    }
    review_flags = {key: path.is_file() for key, path in review_files.items()}

    remaining: list[str] = []
    if pilot_by_track["debug"] == 0:
        remaining.append("E01-real-debug-closed-loop")
    if pilot_by_track["review_release"] == 0:
        remaining.append("E03-real-review-release-closed-loop")
    if r2_qualified == 0:
        remaining.append("E06-real-multi-runtime-qualified-comparison")
    if not evaluated_ids:
        remaining.append("E09-retained-skill-evaluated-summary")
    if real_invocations == 0:
        remaining.append("E10-real-runtime-owned-skill-attribution")

    current_floor = "EVALUATED" if len(evaluated_ids) == len(skills) and skills else "DEFINED"

    snapshot = {
        "schema_version": 1,
        "kind": "edge-foundation-review-snapshot",
        "derived_view": True,
        "authority": "none-derived-from-canonical-assets",
        "sources": [
            "SKILLS.md",
            "domains/edge-foundation/domain.yaml",
            "domains/edge-foundation/routing.yaml",
            "domains/edge-foundation/gate-policy.yaml",
            "domains/edge-foundation/skills.yaml",
            "domains/edge-foundation/evaluation/skill-evaluation-plan.yaml",
            "domains/edge-foundation/evaluation/evidence/",
            "domains/edge-foundation/pilot/evidence/",
            "reports/runtime-r2/freeze/",
        ],
        "architecture": {
            "domain_status": domain["status"],
            "domain_experts": len(domain["experts"]),
            "embedded_capabilities": len(embedded.get("capabilities", [])),
            "task_types": len(routing["routing"]),
            "gates": len(gates["gates"]),
        },
        "skills": {
            "registered": len(skills),
            "review_grade_contracts": review_grade_skill_count(skills),
            "evaluation_plan_skills": len(eval_plan["skills"]),
            "positive_cases": positive,
            "block_cases": block,
            "total_evaluation_cases": positive + block,
            "retained_evaluated_summaries": retained_summaries,
            "evaluated_skill_ids": evaluated_ids,
            "retained_real_invocation_receipts": real_invocations,
            "real_attributed_skill_ids": real_skill_ids,
            "current_claimable_floor": current_floor,
            "skill_portability_proven": False,
        },
        "retained_evidence": {
            "real_pilot_results": pilot_total,
            "real_pilot_pass_results": pilot_pass,
            "real_pilot_pass_by_track": pilot_by_track,
        },
        "runtime_replaceability": {
            "r2_freeze_receipts": r2_freeze,
            "r2_qualified_receipts": r2_qualified,
            "status": r2_status,
            "skill_portability_inherited": False,
        },
        "review_material": {
            "status": "READY" if all(review_flags.values()) else "INCOMPLETE",
            **review_flags,
        },
        "external_decision_status": {
            "product_readiness": "use-dedicated-product-readiness-evaluator",
            "productionization": "use-human-governance-review",
            "note": "This static snapshot does not infer Product readiness, Runtime Qualification, release authority, or Productionization from retained files or CI fixtures.",
        },
        "remaining_evidence_gates": remaining,
    }
    validate_json(snapshot, SCHEMA)
    return snapshot


def render_markdown(snapshot: dict) -> str:
    s = snapshot
    tracks = s["retained_evidence"]["real_pilot_pass_by_track"]
    gates = "\n".join(f"- `{item}`" for item in s["remaining_evidence_gates"]) or "- none detected by this static view"
    evaluated = ", ".join(s["skills"]["evaluated_skill_ids"]) or "none"
    attributed = ", ".join(s["skills"]["real_attributed_skill_ids"]) or "none"
    return f"""# 当前机器状态快照

> **Derived view only — 不是新的 authority。**  
> 生成器：`scripts/generate_edge_foundation_review_snapshot.py`。  
> 机器 JSON：`reports/review/edge-foundation-review-snapshot.json`。

本页用于正式评审快速回答“当前仓库静态事实到哪一步”。它不会从 CI fixture、文件存在、R2 freeze 或 Pilot result 自动推导 Product readiness、Runtime Qualification、Skill maturity、Release Ready 或 Productionization。

## 1. 架构与评审材料

| 项目 | 当前机器事实 |
|---|---:|
| Domain status | `{s['architecture']['domain_status']}` |
| Domain Experts | {s['architecture']['domain_experts']} |
| Embedded Capabilities | {s['architecture']['embedded_capabilities']} |
| Canonical task types | {s['architecture']['task_types']} |
| Gates | {s['architecture']['gates']} |
| Review material | **{s['review_material']['status']}** |

Review material = READY 只表示正式评审入口/索引/台账/检查表存在，不表示工程成熟或产品可发布。

## 2. Skill 静态与证据状态

| 项目 | 当前机器事实 |
|---|---:|
| Canonical Skills | {s['skills']['registered']} |
| Review-grade Skill contracts | {s['skills']['review_grade_contracts']} |
| Evaluation plan Skills | {s['skills']['evaluation_plan_skills']} |
| Positive cases | {s['skills']['positive_cases']} |
| BLOCK cases | {s['skills']['block_cases']} |
| Total Skill evaluation cases | {s['skills']['total_evaluation_cases']} |
| Retained evaluation summaries | {s['skills']['retained_evaluated_summaries']} |
| Retained real Skill invocation receipts | {s['skills']['retained_real_invocation_receipts']} |
| Current claimable floor | **{s['skills']['current_claimable_floor']}** |
| Skill portability proven | **{str(s['skills']['skill_portability_proven']).lower()}** |

Retained EVALUATED Skill IDs: **{evaluated}**  
Real-attributed Skill IDs: **{attributed}**

当前如果没有 retained positive + BLOCK semantic evidence summary，就继续保持 DEFINED；CI synthetic case 只证明评测机制。

## 3. 仓内保留的真实 Pilot 结果

| Track | retained real PASS result |
|---|---:|
| Debug | {tracks['debug']} |
| Feature | {tracks['feature']} |
| Review / Release | {tracks['review_release']} |

这里统计的是**仓库内保留的 `pilot-result.json`**，不是 Product readiness eligible receipt。Product readiness 必须由 `evaluate_edge_foundation_product_readiness.py` 的独立 receipt/evaluator 证明。

## 4. Runtime R2 与 Skill Portability

| 项目 | 当前机器事实 |
|---|---:|
| R2 freeze receipts | {s['runtime_replaceability']['r2_freeze_receipts']} |
| R2 qualified receipts retained | {s['runtime_replaceability']['r2_qualified_receipts']} |
| R2 retained state | `{s['runtime_replaceability']['status']}` |
| Skill portability inherited from R2 | **false** |

Runtime R2 campaign 证明 Runtime replaceability 的独立轴；即使 R2 后续 qualified，也不能自动提升具体 Skill portability，除非同一 frozen Skill Contract 在两个 Runtime 上有可比 positive/BLOCK/evaluation evidence。

## 5. 当前仍需真实 Evidence 关闭的 Gate

{gates}

这些是静态 snapshot 能直接识别的证据缺口。完整治理状态仍以 Decision/Evidence Register、各独立 evaluator 和正式人工评审为准。

## 6. 评审结论边界

当前可以区分为：

- **评审材料与框架：READY**；
- **23 个 Skill 定义与 46 个评测场景：结构闭环**；
- **Skill EVALUATED / real PILOTED / portability：按 retained evidence 单独判定**；
- **Product readiness：由专用 evaluator 判定，本快照不推导**；
- **Productionization：由治理硬门 + 人工评审判定，本快照不推导**。

因此不能写“评审材料 READY = 体系成熟落地”。正式结论必须继续绑定 exact evidence scope。
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--check-json", type=Path)
    parser.add_argument("--check-markdown", type=Path)
    args = parser.parse_args()

    snapshot = build_snapshot()
    json_text = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    md_text = render_markdown(snapshot)

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json_text, encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(md_text, encoding="utf-8")
    if args.check_json:
        if args.check_json.read_text(encoding="utf-8") != json_text:
            raise SystemExit("review snapshot JSON is stale; regenerate it")
    if args.check_markdown:
        if args.check_markdown.read_text(encoding="utf-8") != md_text:
            raise SystemExit("review snapshot markdown is stale; regenerate it")
    if not any([args.json_output, args.markdown_output, args.check_json, args.check_markdown]):
        print(json_text, end="")


if __name__ == "__main__":
    main()
