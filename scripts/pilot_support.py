"""Internal Pilot helpers; no CLI and no cached evidence verdicts."""
from __future__ import annotations

import contextvars
import functools
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

_context = contextvars.ContextVar("pilot_validation", default=None)


def validation_scope(function):
    @functools.wraps(function)
    def scoped(*args, **kwargs):
        if _context.get() is not None:
            return function(*args, **kwargs)
        token = _context.set({})
        try:
            return function(*args, **kwargs)
        finally:
            _context.reset(token)
    return scoped


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path):
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_json(value, schema_path: Path):
    from jsonschema import Draft202012Validator
    # Always read the schema. Even a changed schema within one call invalidates
    # its compiled validator; instance/artifact validation is never memoized.
    raw = schema_path.read_bytes()
    key = (str(schema_path.resolve()), hashlib.sha256(raw).digest())
    cache = _context.get()
    validator = cache.get(key) if cache is not None else None
    if validator is None:
        schema = json.loads(raw)
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        if cache is not None:
            cache[key] = validator
    validator.validate(value)


def sanitize_uri(value: str | None) -> str | None:
    if value is None:
        return None
    if any(unicodedata.category(char) == "Cc" for char in value):
        return "[invalid-source-uri]"
    if "://" in value:
        try:
            parts = urlsplit(value)
            # Preserve host/port spelling, remove all userinfo and URL options.
            host = parts.netloc.rsplit("@", 1)[-1]
            return urlunsplit((parts.scheme, host, parts.path, "", ""))
        except ValueError:
            return "[invalid-source-uri]"
    # scp-style Git identity: user@host:path; username is not needed for identity.
    value = re.sub(r"^[^/@:]+@(?=[^/]+:)", "", value)
    return value.split("?", 1)[0].split("#", 1)[0]


def redact_text(value: str) -> str:
    return re.sub(r"[A-Za-z][A-Za-z0-9+.-]*://[^\s\"'<>]+",
                  lambda match: sanitize_uri(match.group(0)) or "", value)


class PilotError(ValueError):
    def __init__(self, code: str, message: str, *, field_path=None, exit_code=2):
        super().__init__(message)
        self.code, self.field_path, self.exit_code = code, field_path, exit_code


def error_result(exc: Exception) -> tuple[dict, int]:
    code = getattr(exc, "code", None)
    if not isinstance(code, str):
        code = "NOT_FOUND" if isinstance(exc, FileNotFoundError) else "VALIDATION_FAILED"
        if isinstance(exc, OSError) and not isinstance(exc, FileNotFoundError):
            code = "IO_ERROR"
    field = getattr(exc, "field_path", None)
    if field is None and hasattr(exc, "absolute_path"):
        field = list(exc.absolute_path)
    if hasattr(exc, "validator") and hasattr(exc, "absolute_path"):
        message = f"JSON validation failed: {exc.validator} constraint at {field}"
        if exc.validator == "required" and isinstance(exc.instance, dict):
            missing = [key for key in exc.validator_value if key not in exc.instance]
            message += "; missing fields: " + ", ".join(str(key)[:64] for key in missing[:5])
    else:
        message = str(exc)
    actions = ["执行 recover --dry-run 检查已提交状态；不要盲目重试或回退证据。"] if code.startswith("COMMIT_") else ["检查输入路径、材料绑定和 doctor 结果；修复后重试。"]
    return {"error_code": code, "message": redact_text(message), "field_path": field,
            "next_actions": actions}, getattr(exc, "exit_code", 1)
