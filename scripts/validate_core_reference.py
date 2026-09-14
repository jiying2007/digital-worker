#!/usr/bin/env python3
"""Validate the human-facing embedded-system core reference against machine baselines."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "嵌入式系统专家团-核心参考"
EMB = ROOT / "expert-groups" / "embedded-system"


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def read(rel: str) -> str:
    return (CORE / rel).read_text(encoding="utf-8")


def main() -> None:
    required = [
        "README.md",
        "00-评审入口/01 评审说明与决策清单.md",
        "01-架构设计/01 总体架构设计.md",
        "01-架构设计/02 系统边界与控制面.md",
        "01-架构设计/03 身份证据与知识架构.md",
        "02-流程与运行/01 任务生命周期与Gate.md",
        "02-流程与运行/02 Debug问题闭环流程.md",
        "02-流程与运行/03 功能开发Bring-up与多仓协同.md",
        "02-流程与运行/04 验证评审发布与异常恢复.md",
        "03-角色与领域/01 组织模型职责与RACI.md",
        "03-角色与领域/02 架构LinuxBSPMCURTOS与驱动领域指南.md",
        "03-角色与领域/03 调试验证与独立评审领域指南.md",
        "04-工程交付/01 Skill能力地图.md",
        "04-工程交付/02 工程交接Runtime与关键产物.md",
        "05-治理与评测/01 权限安全风险与例外.md",
        "05-治理与评测/02 Pilot指标成熟度与生产化.md",
        "05-治理与评测/03 架构取舍与演进原则.md",
        "06-案例/01 UBIFS只读问题走查.md",
        "06-案例/02 多仓功能与OTA发布走查.md",
    ]
    for rel in required:
        path = CORE / rel
        require(path.is_file(), f"missing core reference: {rel}")
        require(len(path.read_text(encoding='utf-8').strip()) >= 500, f"core reference too thin: {rel}")

    index = read("README.md")
    require("operational reference" in index, "core reference must declare operational reference status")
    require("v0.7.0" in index, "core reference must declare v0.7.0")
    require("iterative-development" in index, "core reference must state current repository stage")

    expert_group = yaml.safe_load((EMB / "expert-group.yaml").read_text(encoding="utf-8"))
    require(expert_group["version"] == "0.7.0", "unexpected embedded expert-group version")
    require(expert_group["architecture_model"] == "provider-neutral", "embedded architecture must remain provider-neutral")
    require(len(expert_group["experts"]) == 7, "human reference assumes 1+7 expert organization")

    skill_registry = yaml.safe_load((EMB / "config/p0-skills.yaml").read_text(encoding="utf-8"))
    skills = [item["id"] for item in skill_registry["skills"]]
    require(len(skills) == 23, f"expected 23 P0 skills, got {len(skills)}")
    skill_doc = read("04-工程交付/01 Skill能力地图.md")
    missing_skills = [skill for skill in skills if skill not in skill_doc]
    require(not missing_skills, f"skill map missing registered skills: {missing_skills}")

    architecture = read("01-架构设计/01 总体架构设计.md")
    require("1+7" in architecture, "architecture must explain 1+7 organization")
    require("Provider-neutral" in architecture, "architecture must explain provider-neutral behavior")
    require("四个稳定控制面 + N 个 Runtime Binding" in architecture, "architecture must explain control-plane model")

    identity = read("01-架构设计/03 身份证据与知识架构.md")
    require("Source of Truth stays at source" in identity, "identity/knowledge doc must retain source authority rule")
    require("Acceptance → Evidence" in identity, "identity/knowledge doc must explain acceptance-evidence mapping")

    workflow = read("02-流程与运行/01 任务生命周期与Gate.md")
    for gate in ["Gate K", "Gate M", "Gate 0", "Gate T", "Gate E", "Gate V", "Gate R", "Gate C"]:
        require(gate in workflow, f"workflow doc missing {gate}")

    safety = read("05-治理与评测/01 权限安全风险与例外.md")
    for level in [f"A{i}" for i in range(8)]:
        require(level in safety, f"safety doc missing {level}")

    pilot = read("05-治理与评测/02 Pilot指标成熟度与生产化.md")
    for marker in ["incorrect_pass_rate = 0", "unauthorized_actions = 0", "audit_trace_completeness = 1.0", "E2 Engineering Closed Loop", "E3 Knowledge Closed Loop"]:
        require(marker in pilot, f"pilot/maturity doc missing marker: {marker}")

    review = read("00-评审入口/01 评审说明与决策清单.md")
    for decision in [f"D{i:02d}" for i in range(1, 11)]:
        require(decision in review, f"review guide missing decision: {decision}")

    stale_root_files = [path.name for path in CORE.glob("[0-9][0-9] *.md")]
    require(not stale_root_files, f"legacy flat core-reference files must be removed: {stale_root_files}")
    require(not (ROOT / "docs/review").exists(), "legacy docs/review pack must be removed")

    forbidden = ["review-ready", "01~16 已统一", "v0.6.0"]
    violations = []
    for path in CORE.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                violations.append(f"{path.relative_to(ROOT)} -> {token}")
    require(not violations, "stale core-reference wording found: " + "; ".join(violations))

    print("core reference validation PASS: operational human reference synchronized with embedded v0.7.0")


if __name__ == "__main__":
    main()
