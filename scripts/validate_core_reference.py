#!/usr/bin/env python3
"""Fail-closed consistency checks for the embedded core-reference review pack."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "嵌入式系统专家团-核心参考"


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def read(name: str) -> str:
    return (CORE / name).read_text(encoding="utf-8")


def main() -> None:
    expected = [
        "README.md",
        "01 嵌入式系统专家团整体架构.md",
        "02 主理人专家工作逻辑.md",
        "11 Workflow、Gate 与工程交接.md",
        "12 Evidence、知识、自治与安全边界.md",
        "13 Pilot、评测与生产化评审.md",
        "14 跨专家团协作与职责边界.md",
        "15 内部评审问题清单.md",
        "16 总体架构与Provider选型评审.md",
    ]
    for name in expected:
        require((CORE / name).is_file(), f"missing core reference: {name}")

    index = read("README.md")
    require("v0.7.0" in index, "core reference index must declare v0.7.0")
    require("provider-neutral" in index.lower(), "core reference index must declare provider-neutral architecture")
    require("01~16 已统一" in index, "core reference index must state full synchronization")

    synced = expected[1:8]
    for name in synced:
        text = read(name)
        require("v0.7.0 / provider-neutral" in text, f"{name} missing v0.7.0 provider-neutral sync marker")

    forbidden = {
        "Engineer + Codex": "fixed Codex execution role",
        "Engineer+Codex": "fixed Codex execution role",
        "飞书：人工正式知识主库": "fixed Feishu canonical knowledge role",
        "飞书 canonical + WeKnora retrieval": "fixed Feishu/WeKnora topology",
        "飞书是人工 canonical knowledge": "fixed Feishu canonical knowledge role",
        "WorkBuddy 不直接遥控个人 Codex": "provider-specific handoff wording",
        "v0.6.0": "stale implementation baseline",
        "main@fba5e1a607619112783fdf89e8bdf0d1b481626f": "stale synchronization SHA",
    }
    violations = []
    for name in synced:
        text = read(name)
        for token, reason in forbidden.items():
            if token in text:
                violations.append(f"{name}: {reason}: {token}")
    require(not violations, "stale provider-specific core-reference statements: " + "; ".join(violations))

    require("Engineering Agent Runtime" in read("11 Workflow、Gate 与工程交接.md"), "handoff doc must use generic Engineering Agent Runtime")
    require("Source of Truth stays at source" in read("12 Evidence、知识、自治与安全边界.md"), "knowledge doc must use source-of-truth principle")
    require("Multi-runtime Pilot" in read("13 Pilot、评测与生产化评审.md"), "pilot doc must include multi-runtime validation")
    require("Knowledge Provider / Sources" in read("14 跨专家团协作与职责边界.md"), "cross-team doc must separate knowledge provider/source")
    require("Provider Capability Matrix" in read("15 内部评审问题清单.md"), "review checklist must include provider capability matrix")

    print("core reference validation PASS: v0.7.0 provider-neutral review pack synchronized")


if __name__ == "__main__":
    main()
