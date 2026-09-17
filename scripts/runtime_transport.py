#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config/integrations/runtime-transport-profiles.json"


class TransportBlocked(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TransportBlocked("transport config must be a JSON object")
    if value.get("schema_version") != 1:
        raise TransportBlocked("unsupported transport config schema")
    return value


def resolve(
    config: dict[str, Any],
    *,
    runtime: str,
    profile: str,
    environment: str,
    endpoint: str,
    credential_present: bool,
) -> dict[str, Any]:
    runtimes = config.get("runtimes")
    if not isinstance(runtimes, dict) or runtime not in runtimes:
        raise TransportBlocked(f"unsupported runtime: {runtime}")
    runtime_doc = runtimes[runtime]
    profiles = runtime_doc.get("profiles")
    if not isinstance(profiles, dict) or profile not in profiles:
        raise TransportBlocked(f"unsupported transport profile for {runtime}: {profile}")
    selected = profiles[profile]
    allowed = selected.get("allowed_environments")
    if not isinstance(allowed, list) or environment not in allowed:
        raise TransportBlocked(f"transport profile {runtime}/{profile} is not allowed in {environment}")

    endpoint_mode = selected.get("endpoint_mode")
    endpoint = endpoint.strip()
    if endpoint_mode == "configured-relay" and not endpoint:
        raise TransportBlocked(f"transport profile {runtime}/{profile} requires a configured endpoint")
    if endpoint_mode == "official-default" and endpoint:
        raise TransportBlocked(f"transport profile {runtime}/{profile} must not override the official endpoint")

    credential_requirement = selected.get("credential_requirement")
    if credential_requirement == "required" and not credential_present:
        raise TransportBlocked(f"transport profile {runtime}/{profile} requires external credential material")
    if credential_requirement == "none-from-digital-worker" and credential_present:
        raise TransportBlocked(f"transport profile {runtime}/{profile} must use runtime-owned authentication")

    endpoint_class = {
        "configured-relay": "configured-relay",
        "official-default": "official-default",
        "runtime-default": "runtime-owned-default",
    }.get(str(endpoint_mode), "unknown")
    endpoint_sha = _sha256_text(endpoint) if endpoint else None
    gateway_material = {
        "runtime": runtime,
        "runtime_target": runtime_doc.get("runtime_target"),
        "transport_profile": profile,
        "transport_kind": selected.get("transport_kind"),
        "protocol": selected.get("protocol"),
        "credential_mode": selected.get("credential_mode"),
        "endpoint_class": endpoint_class,
        "endpoint_sha256": endpoint_sha,
        "environment": environment,
    }
    gateway_identity = hashlib.sha256(_canonical(gateway_material)).hexdigest()
    return {
        "schema": "digital-worker-runtime-transport-resolution/v1",
        "status": "ready",
        **gateway_material,
        "credential_present": credential_present,
        "gateway_identity_sha256": gateway_identity,
        "r2_github_hosted_eligible": bool(selected.get("r2_github_hosted_eligible")),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve provider-neutral runtime transport profiles without persisting secrets.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--runtime", required=True, choices=("codex", "claude-code"))
    parser.add_argument("--profile", required=True)
    parser.add_argument("--environment", required=True, choices=("developer-workstation", "github-hosted", "self-hosted-runner"))
    parser.add_argument("--endpoint", default="")
    parser.add_argument("--credential-present", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    try:
        config = _load(Path(args.config))
        result = resolve(
            config,
            runtime=args.runtime,
            profile=args.profile,
            environment=args.environment,
            endpoint=args.endpoint,
            credential_present=args.credential_present,
        )
    except (OSError, json.JSONDecodeError, TransportBlocked) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "pass", "output": str(output), "gateway_identity_sha256": result["gateway_identity_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
