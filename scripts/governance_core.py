"""Core validation primitives for the OpenCoven governance plane."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")
EVENT_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
JOB_ID = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
PLAIN_YAML_KEY = re.compile(r"^[A-Za-z0-9_.-]+$")
JOB_LEVEL_REUSABLE_USE = re.compile(
    r"^(?:"
    r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/\.github/workflows/[A-Za-z0-9_.-]+\.ya?ml@[^\s{}\[\],#]+"
    r"|"
    r"\./\.github/workflows/[A-Za-z0-9_.\/-]+\.ya?ml"
    r")$"
)
ACTION_USE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)
DOCKER_DIGEST_USE = re.compile(r"^docker://[^@\s]+@sha256:[0-9a-fA-F]{64}$")
FLOW_STYLE_ACTION_USE = re.compile(
    r"^(?:\s*steps\s*:\s*\[[^\n]*|\s*-?\s*\{)[^}\n]*\buses\s*:",
    re.MULTILINE,
)
CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f]")
REUSABLE_WORKFLOWS = {
    "reusable-agent-readiness.yml",
    "reusable-evidence-packet.yml",
}
SECRET_PATTERNS = {
    # Fragmented construction avoids embedding credential-shaped examples in this
    # public source file while preserving the exact detector semantics.
    "GitHub token": re.compile(
        r"\b(?:g" + r"h[pousr]_" + r"[A-Za-z0-9_]{20,}|github_"
        + r"pat_" + r"[A-Za-z0-9_]{20,})\b"
    ),
    "AWS access key": re.compile(r"\b(?:A" + r"KIA|ASIA)[A-Z0-9]{16}\b"),
    "private key": re.compile("-" * 5 + r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY" + "-" * 5),
    "OpenAI-style secret": re.compile(r"\bs" + r"k-(?:proj-)?[A-Za-z0-9_-]{24,}\b"),
}
TEXT_SUFFIXES = {".md", ".json", ".yml", ".yaml", ".py", ".sh", ".txt"}

class DuplicateKeyError(ValueError):
    pass


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicate_keys)
    except (OSError, json.JSONDecodeError, DuplicateKeyError) as exc:
        raise ValueError(f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}: {exc}") from exc


def validate_json_schema(instance: Any, schema: dict[str, Any], *, label: str) -> list[str]:
    errors: list[str] = []

    def visit(value: Any, rule: dict[str, Any], path: str) -> None:
        expected_type = rule.get("type")
        if expected_type:
            matches = {
                "object": isinstance(value, dict),
                "array": isinstance(value, list),
                "string": isinstance(value, str),
                "boolean": isinstance(value, bool),
                "integer": isinstance(value, int) and not isinstance(value, bool),
                "number": isinstance(value, (int, float)) and not isinstance(value, bool),
                "null": value is None,
            }.get(expected_type)
            if matches is None:
                errors.append(f"{path}: schema uses unsupported type {expected_type!r}")
                return
            if not matches:
                errors.append(f"{path}: schema expected {expected_type}, got {type(value).__name__}")
                return

        if "const" in rule and value != rule["const"]:
            errors.append(f"{path}: schema expected constant {rule['const']!r}, got {value!r}")
        if "enum" in rule and value not in rule["enum"]:
            errors.append(f"{path}: schema value {value!r} is not in {rule['enum']!r}")

        if isinstance(value, str):
            if len(value) < rule.get("minLength", 0):
                errors.append(f"{path}: schema string is shorter than minLength {rule['minLength']}")
            pattern = rule.get("pattern")
            if pattern is not None and re.search(pattern, value) is None:
                errors.append(f"{path}: schema string does not match pattern {pattern!r}")
            if rule.get("format") == "date":
                try:
                    date.fromisoformat(value)
                except ValueError:
                    errors.append(f"{path}: schema expected ISO date, got {value!r}")

        if isinstance(value, (int, float)) and not isinstance(value, bool) and "minimum" in rule:
            if value < rule["minimum"]:
                errors.append(f"{path}: schema value is below minimum {rule['minimum']}")

        if isinstance(value, list):
            if len(value) < rule.get("minItems", 0):
                errors.append(f"{path}: schema array has fewer than {rule['minItems']} items")
            if rule.get("uniqueItems"):
                encoded = [json.dumps(item, sort_keys=True, separators=(",", ":")) for item in value]
                if len(encoded) != len(set(encoded)):
                    errors.append(f"{path}: schema array items must be unique")
            item_rule = rule.get("items")
            if isinstance(item_rule, dict):
                for index, item in enumerate(value):
                    visit(item, item_rule, f"{path}[{index}]")

        if isinstance(value, dict):
            properties = rule.get("properties", {})
            for required in rule.get("required", []):
                if required not in value:
                    errors.append(f"{path}.{required}: schema required property is missing")
            if rule.get("additionalProperties") is False:
                for key in value:
                    if key not in properties:
                        errors.append(f"{path}.{key}: schema additional property is not allowed")
            for key, child_rule in properties.items():
                if key in value and isinstance(child_rule, dict):
                    visit(value[key], child_rule, f"{path}.{key}")

    visit(instance, schema, label)
    return errors


def _prefix_parts(prefix: str) -> tuple[str, ...]:
    parsed = PurePosixPath(prefix)
    return tuple(part for part in parsed.parts if part not in {"", "."})


def _clean_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _event_name(value: str, *, label: str) -> str:
    if not value or value[0] in {"!", ">", "|"}:
        raise ValueError(f"{label}: unsupported event scalar syntax")
    if not EVENT_NAME.fullmatch(value):
        raise ValueError(f"{label}: event names must be plain or unescaped quoted ASCII identifiers")
    return value


def _is_yaml_content(line: str) -> bool:
    return bool(line.strip() and not line.lstrip().startswith("#"))


def resolve_trusted_target_file(
    target_root: Path,
    relative_path: str,
    *,
    label: str,
    required_prefix: str | None = None,
    required_suffixes: tuple[str, ...] = (),
) -> Path:
    """Resolve a caller-provided repository-relative path without following symlinks.

    The reusable workflows validate files from a caller repository checkout.
    Those paths are untrusted workflow inputs, so they must remain literal
    repository-relative paths: no absolute paths, traversal, control
    characters, symlink components, missing paths, directories, or special
    files are accepted.
    """
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise ValueError(f"{label}: path is required")
    if CONTROL_CHARACTERS.search(relative_path):
        raise ValueError(f"{label}: control characters are forbidden")
    if "\\" in relative_path:
        raise ValueError(f"{label}: use repository-relative POSIX paths")
    parsed = PurePosixPath(relative_path)
    if parsed.is_absolute():
        raise ValueError(f"{label}: absolute paths are forbidden")
    parts = parsed.parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"{label}: traversal and empty path components are forbidden")
    if required_prefix:
        prefix = _prefix_parts(required_prefix)
        if tuple(parts[:len(prefix)]) != prefix:
            raise ValueError(f"{label}: path must be under {required_prefix}/")
    if required_suffixes and not any(parts[-1].endswith(suffix) for suffix in required_suffixes):
        suffixes = ", ".join(required_suffixes)
        raise ValueError(f"{label}: path must end with one of: {suffixes}")

    try:
        root = target_root.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"{label}: target root is not accessible: {exc}") from exc
    if not root.is_dir():
        raise ValueError(f"{label}: target root is not a directory")

    current = root
    for index, part in enumerate(parts):
        current = current / part
        if current.is_symlink():
            raise ValueError(f"{label}: symlink path components are forbidden: {PurePosixPath(*parts[:index + 1])}")
        if not current.exists():
            raise ValueError(f"{label}: file does not exist: {relative_path}")
        if index < len(parts) - 1 and not current.is_dir():
            raise ValueError(f"{label}: non-directory path component: {PurePosixPath(*parts[:index + 1])}")
    if not current.is_file():
        raise ValueError(f"{label}: path is not a regular file: {relative_path}")
    try:
        resolved = current.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"{label}: file is not accessible: {exc}") from exc
    if not resolved.is_relative_to(root):
        raise ValueError(f"{label}: resolved path escapes the target root")
    return current


def _strip_yaml_comment(value: str) -> str:
    quote: str | None = None
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if quote == '"' and char == "\\":
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            continue
        if char == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.rstrip()


def _yaml_key_value(line: str) -> tuple[int, str, str | None] | None:
    parts = _yaml_key_value_parts(line)
    if not parts:
        return None
    indent, _raw_key, key, _raw_value, value = parts
    return indent, key, value


def _yaml_key_value_parts(line: str) -> tuple[int, str, str, str | None, str | None] | None:
    if not line.strip() or line.lstrip().startswith("#"):
        return None
    if "\t" in line:
        raise ValueError("YAML tabs are unsupported in reusable workflow policy checks")
    raw = _strip_yaml_comment(line)
    key = r"(?:[A-Za-z0-9_.-]+|'[^']+'|\"[^\"]+\")"
    match = re.match(rf"^(?P<indent> *)(?P<key>{key}):(?P<value>(?:\s+.*)?)$", raw)
    if not match:
        return None
    value = match.group("value")
    raw_key = match.group("key")
    raw_value = value.strip() if value and value.strip() else None
    return (
        len(match.group("indent")),
        raw_key,
        _clean_scalar(raw_key),
        raw_value,
        _clean_scalar(raw_value) if raw_value else None,
    )


def _yaml_sequence_item(line: str) -> tuple[int, str] | None:
    if not line.strip() or line.lstrip().startswith("#"):
        return None
    if "\t" in line:
        raise ValueError("YAML tabs are unsupported in reusable workflow policy checks")
    raw = _strip_yaml_comment(line)
    match = re.match(r"^(?P<indent> *)-\s+(?P<value>.+)$", raw)
    if not match:
        return None
    return len(match.group("indent")), _clean_scalar(match.group("value"))


def _parse_flow_sequence(value: str, *, label: str) -> list[str]:
    text = value.strip()
    if not text.startswith("[") or not text.endswith("]"):
        raise ValueError(f"{label}: unsupported flow sequence syntax")
    inner = text[1:-1].strip()
    if not inner:
        return []
    items: list[str] = []
    token: list[str] = []
    quote: str | None = None
    escaped = False
    for char in inner:
        if escaped:
            token.append(char)
            escaped = False
            continue
        if quote == '"' and char == "\\":
            token.append(char)
            escaped = True
            continue
        if quote:
            token.append(char)
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            token.append(char)
            continue
        if char == ",":
            item = "".join(token).strip()
            if not item:
                raise ValueError(f"{label}: empty flow sequence items are unsupported")
            items.append(_clean_scalar(item))
            token = []
            continue
        if char in "{}[]":
            raise ValueError(f"{label}: nested flow YAML is unsupported")
        token.append(char)
    if quote:
        raise ValueError(f"{label}: unterminated quoted scalar")
    item = "".join(token).strip()
    if not item:
        raise ValueError(f"{label}: empty flow sequence items are unsupported")
    items.append(_clean_scalar(item))
    return items


def _top_level_block(lines: list[str], key: str) -> tuple[str | None, list[str]]:
    found: tuple[str | None, list[str]] | None = None
    for index, line in enumerate(lines):
        item = _yaml_key_value_parts(line)
        if not item:
            continue
        indent, raw_key, item_key, _raw_value, value = item
        if indent == 0 and item_key == key:
            if raw_key != key:
                raise ValueError(f"top-level YAML key must be plain for policy checks: {key}")
            if found is not None:
                raise ValueError(f"duplicate top-level YAML key is unsupported: {key}")
            block: list[str] = []
            for child in lines[index + 1:]:
                child_item = _yaml_key_value(child)
                if child_item and child_item[0] == 0:
                    break
                block.append(child)
            found = (value, block)
    return found if found is not None else (None, [])


def _block_contains_key(block: list[str], key: str) -> bool:
    for line in block:
        item = _yaml_key_value(line)
        if item and item[1] == key:
            return True
    return False


def _workflow_declares_workflow_call(lines: list[str]) -> bool:
    value, block = _top_level_block(lines, "on")
    events: list[str] = []
    if value is not None:
        if any(_is_yaml_content(line) for line in block):
            raise ValueError("caller workflow on: unsupported continuation lines after scalar event declaration")
        if value.startswith("{"):
            raise ValueError("caller workflow on: flow mappings are unsupported")
        if value.startswith("["):
            events.extend(
                _event_name(event, label="caller workflow on")
                for event in _parse_flow_sequence(value, label="caller workflow on")
            )
        elif any(char in value for char in "{}[]"):
            raise ValueError("caller workflow on: unsupported flow YAML syntax")
        else:
            events.append(_event_name(_clean_scalar(value), label="caller workflow on"))
    else:
        entries: list[tuple[int, str, str, str | None]] = []
        for line in block:
            sequence = _yaml_sequence_item(line)
            if sequence:
                indent, sequence_value = sequence
                entries.append((indent, "sequence", sequence_value, None))
                continue
            item = _yaml_key_value(line)
            if item:
                indent, key, item_value = item
                entries.append((indent, "mapping", key, item_value))
                continue
            if _is_yaml_content(line):
                raise ValueError("caller workflow on: unsupported continuation or scalar syntax")
        if not entries:
            raise ValueError("caller workflow must declare on using a supported literal event form")
        event_indent = min(indent for indent, *_ in entries)
        direct = [entry for entry in entries if entry[0] == event_indent]
        kinds = {kind for _, kind, _, _ in direct}
        if len(kinds) != 1:
            raise ValueError("caller workflow on: mixed sequence and mapping forms are unsupported")
        seen: set[str] = set()
        for _, kind, event, event_value in direct:
            if event in seen:
                raise ValueError(f"caller workflow on: duplicate event key is unsupported: {event}")
            seen.add(event)
            if kind == "sequence" and any(char in event for char in "{}[]"):
                raise ValueError("caller workflow on: unsupported sequence item syntax")
            if event.startswith(("!", ">", "|")):
                raise ValueError("caller workflow on: unsupported event scalar syntax")
            if kind == "mapping" and event_value is not None and event_value.startswith("{"):
                raise ValueError("caller workflow on: flow mappings are unsupported")
            if kind == "mapping" and event_value is not None and event_value.startswith(("!", ">", "|")):
                raise ValueError("caller workflow on: unsupported event value scalar syntax")
            events.append(_event_name(_clean_scalar(event), label="caller workflow on"))
    if "pull_request_target" in events:
        raise ValueError("caller workflow pull_request_target is forbidden")
    return "workflow_call" in events


def _contains_yaml_anchor_or_alias(text: str) -> bool:
    if re.search(r"(?m)^\s*<<\s*:", text):
        return True
    return bool(re.search(r"(?<![\w/.-])[*&][A-Za-z_][A-Za-z0-9_-]*\b", text))


def _scalar_has_expression(value: str | None) -> bool:
    return bool(value and "${{" in value)


def _line_indent(line: str) -> int:
    if "\t" in line:
        raise ValueError("YAML tabs are unsupported in reusable workflow policy checks")
    return len(line) - len(line.lstrip(" "))


def _validate_plain_security_key(raw_key: str, key: str, *, label: str) -> None:
    if raw_key != key:
        raise ValueError(f"{label}: quoted security-relevant keys are unsupported: {key}")
    if not PLAIN_YAML_KEY.fullmatch(raw_key):
        raise ValueError(f"{label}: unsupported security-relevant key syntax: {key}")


def _validate_security_scalar(raw_value: str | None, value: str | None, *, label: str) -> None:
    if raw_value is None or value is None:
        raise ValueError(f"{label}: literal scalar value is required")
    raw = raw_value.strip()
    if not raw:
        raise ValueError(f"{label}: literal scalar value is required")
    if raw.startswith(("!", ">", "|", "&", "*")):
        raise ValueError(f"{label}: YAML tags, block scalars, anchors, and aliases are unsupported")
    if raw[0] in {"'", '"'}:
        raise ValueError(f"{label}: quoted scalars are unsupported")
    if any(char in raw for char in "{}[]"):
        raise ValueError(f"{label}: flow YAML values are unsupported")


def _block_has_yaml_content(block: list[str]) -> bool:
    return any(_is_yaml_content(line) for line in block)


def _direct_child_properties(
    block: list[str],
    parent_indent: int,
    *,
    label: str = "caller job",
) -> dict[str, tuple[str | None, list[str]]]:
    child_items = []
    unsupported_items: list[tuple[int, int, str]] = []
    for offset, line in enumerate(block):
        if not _is_yaml_content(line):
            continue
        indent = _line_indent(line)
        item = _yaml_key_value_parts(line)
        if item and item[0] > parent_indent:
            child_items.append((offset, *item))
        elif indent > parent_indent:
            unsupported_items.append((offset, indent, line.strip()))
    if not child_items:
        if unsupported_items:
            raise ValueError(f"{label}: unsupported direct job mapping syntax")
        return {}
    child_indent = min(item[1] for item in child_items)
    if any(indent <= child_indent for _offset, indent, _text in unsupported_items):
        raise ValueError(f"{label}: unsupported direct job mapping syntax")
    starts = [
        (offset, raw_key, key, raw_value, value)
        for offset, indent, raw_key, key, raw_value, value in child_items
        if indent == child_indent
    ]
    result: dict[str, tuple[str | None, list[str]]] = {}
    for index, (offset, raw_key, key, raw_value, value) in enumerate(starts):
        if key in result:
            raise ValueError(f"duplicate caller job YAML key is unsupported: {key}")
        end = starts[index + 1][0] if index + 1 < len(starts) else len(block)
        child_block = block[offset + 1:end]
        if key in {"uses", "with", "secrets"}:
            _validate_plain_security_key(raw_key, key, label=label)
            if key == "uses":
                _validate_security_scalar(raw_value, value, label=f"{label}: uses")
                if _block_has_yaml_content(child_block):
                    raise ValueError(f"{label}: uses multiline values are unsupported")
                if value and not JOB_LEVEL_REUSABLE_USE.fullmatch(value):
                    raise ValueError(f"{label}: uses must be a canonical literal reusable workflow reference")
            elif key == "with" and value is not None:
                _validate_security_scalar(raw_value, value, label=f"{label}: with")
            elif key == "secrets" and value is not None:
                _validate_security_scalar(raw_value, value, label=f"{label}: secrets")
        result[key] = (value, child_block)
    return result


def _mapping_values(block: list[str], parent_indent: int, *, label: str = "caller with") -> dict[str, str | None]:
    child_items = []
    unsupported_items: list[tuple[int, str]] = []
    for line in block:
        if not _is_yaml_content(line):
            continue
        indent = _line_indent(line)
        item = _yaml_key_value_parts(line)
        if item and item[0] > parent_indent:
            child_items.append(item)
        elif indent > parent_indent:
            unsupported_items.append((indent, line.strip()))
    if not child_items:
        if unsupported_items:
            raise ValueError(f"{label}: unsupported input mapping syntax")
        return {}
    child_indent = min(item[0] for item in child_items)
    if any(indent <= child_indent for indent, _text in unsupported_items):
        raise ValueError(f"{label}: unsupported input mapping syntax")
    result: dict[str, str | None] = {}
    for indent, raw_key, key, raw_value, value in child_items:
        if indent != child_indent:
            continue
        _validate_plain_security_key(raw_key, key, label=label)
        if key in result:
            raise ValueError(f"duplicate caller with input is unsupported: {key}")
        _validate_security_scalar(raw_value, value, label=f"{label}.{key}")
        result[key] = value
    return result


def _job_blocks(lines: list[str]) -> list[tuple[str, int, list[str]]]:
    jobs_value, jobs_block = _top_level_block(lines, "jobs")
    if jobs_value is not None:
        raise ValueError("caller workflow jobs: inline mappings are unsupported")
    items = []
    unsupported_items: list[tuple[int, str]] = []
    for offset, line in enumerate(jobs_block):
        if not _is_yaml_content(line):
            continue
        indent = _line_indent(line)
        item = _yaml_key_value(line)
        if item:
            indent, key, value = item
            items.append((offset, indent, key, value))
        else:
            unsupported_items.append((indent, line.strip()))
    if not items:
        if unsupported_items:
            raise ValueError("caller workflow jobs: unsupported job mapping syntax")
        return []
    job_indent = min(indent for _, indent, _, _ in items)
    if any(indent <= job_indent for indent, _text in unsupported_items):
        raise ValueError("caller workflow jobs: unsupported job mapping syntax")
    starts = []
    seen: set[str] = set()
    for offset, indent, key, value in items:
        if indent != job_indent:
            continue
        raw_key = _yaml_key_value_parts(jobs_block[offset])[1]
        if raw_key != key:
            raise ValueError(f"caller workflow jobs: quoted job identifiers are unsupported: {key}")
        if not JOB_ID.fullmatch(key):
            raise ValueError(f"caller workflow jobs: unsupported job identifier syntax: {key}")
        if key in seen:
            raise ValueError(f"duplicate caller job id is unsupported: {key}")
        seen.add(key)
        if value is not None:
            raise ValueError(f"caller job {key}: inline job mappings are unsupported")
        starts.append((offset, key))
    jobs = []
    for index, (offset, key) in enumerate(starts):
        end = starts[index + 1][0] if index + 1 < len(starts) else len(jobs_block)
        jobs.append((key, job_indent, jobs_block[offset + 1:end]))
    return jobs


def _parse_caller_workflow_ref(caller_workflow_ref: str) -> tuple[str, str, str]:
    match = re.fullmatch(r"([^/]+/[^/]+)/(.+)@(.+)", caller_workflow_ref)
    if not match:
        raise ValueError("caller workflow ref must be owner/repo/.github/workflows/file.yml@ref")
    return match.group(1), match.group(2), match.group(3)


def validate_reusable_invocation(
    target_root: Path,
    *,
    caller_workflow_ref: str,
    caller_repository: str,
    policy_ref: str,
    reusable_workflow: str,
    path_input_name: str,
    runtime_path: str,
    default_runtime_path: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if reusable_workflow not in REUSABLE_WORKFLOWS:
        errors.append(f"reusable workflow is not supported: {reusable_workflow}")
    if not SHA40.fullmatch(policy_ref or ""):
        errors.append("policy_ref must be a full immutable commit SHA")
    try:
        ref_repository, workflow_path, _workflow_ref = _parse_caller_workflow_ref(caller_workflow_ref)
    except ValueError as exc:
        return errors + [str(exc)]
    if ref_repository != caller_repository:
        errors.append(f"caller workflow ref repository {ref_repository!r} does not match runtime repository {caller_repository!r}")
    try:
        caller_file = resolve_trusted_target_file(
            target_root,
            workflow_path,
            label="caller workflow",
            required_prefix=".github/workflows",
            required_suffixes=(".yml", ".yaml"),
        )
        if caller_file.parent != target_root.resolve(strict=True) / ".github" / "workflows":
            errors.append("caller workflow path must be a direct file below .github/workflows")
    except ValueError as exc:
        return errors + [str(exc)]

    text = caller_file.read_text(encoding="utf-8")
    if _contains_yaml_anchor_or_alias(text):
        errors.append("caller workflow YAML anchors, aliases, and merge keys are unsupported")
    lines = text.splitlines()
    try:
        if _workflow_declares_workflow_call(lines):
            errors.append("nested reusable workflow callers are unsupported")
        jobs = _job_blocks(lines)
    except ValueError as exc:
        return errors + [str(exc)]

    expected_uses_prefix = f"OpenCoven/.github/.github/workflows/{reusable_workflow}@"
    matches: list[tuple[str, dict[str, tuple[str | None, list[str]]], str]] = []
    try:
        job_properties = [
            (job_id, _direct_child_properties(block, job_indent, label=f"caller job {job_id}"))
            for job_id, job_indent, block in jobs
        ]
    except ValueError as exc:
        return errors + [str(exc)]
    for job_id, props in job_properties:
        uses_value = props.get("uses", (None, []))[0]
        if uses_value is None:
            continue
        if _scalar_has_expression(uses_value):
            errors.append(f"caller job {job_id}: expressions are unsupported in uses")
            continue
        if uses_value.startswith("OpenCoven/.github/.github/workflows/") and not uses_value.startswith(expected_uses_prefix):
            errors.append(f"caller job {job_id}: wrong reusable workflow {uses_value!r}")
            continue
        if not uses_value.startswith(expected_uses_prefix):
            continue
        matches.append((job_id, props, uses_value.removeprefix(expected_uses_prefix)))

    if len(matches) != 1:
        errors.append(f"expected exactly one direct caller job for {reusable_workflow}; found {len(matches)}")
        return errors

    job_id, props, uses_ref = matches[0]
    if not SHA40.fullmatch(uses_ref):
        errors.append(f"caller job {job_id}: reusable workflow ref must be a full immutable commit SHA")
    if uses_ref != policy_ref:
        errors.append(f"caller job {job_id}: uses ref does not match runtime policy_ref")

    secrets_value = props.get("secrets", (None, []))[0]
    if secrets_value == "inherit":
        errors.append(f"caller job {job_id}: secrets: inherit is forbidden")

    with_value, with_block = props.get("with", (None, []))
    if with_value is not None:
        errors.append(f"caller job {job_id}: inline with mappings are unsupported")
        with_inputs: dict[str, str | None] = {}
    else:
        try:
            with_inputs = _mapping_values(with_block, 0, label=f"caller job {job_id}: with")
        except ValueError as exc:
            errors.append(str(exc))
            with_inputs = {}
    allowed_inputs = {"policy_ref", path_input_name}
    for input_name in sorted(set(with_inputs) - allowed_inputs):
        errors.append(f"caller job {job_id}: unsupported with input {input_name}")
    literal_policy_ref = with_inputs.get("policy_ref")
    if literal_policy_ref is None:
        errors.append(f"caller job {job_id}: with.policy_ref is required")
    elif _scalar_has_expression(literal_policy_ref):
        errors.append(f"caller job {job_id}: expressions are unsupported in with.policy_ref")
    elif literal_policy_ref != policy_ref:
        errors.append(f"caller job {job_id}: with.policy_ref does not match runtime policy_ref")
    elif literal_policy_ref != uses_ref:
        errors.append(f"caller job {job_id}: with.policy_ref does not match reusable workflow uses ref")

    literal_path = with_inputs.get(path_input_name)
    if literal_path is None:
        literal_path = default_runtime_path
    if literal_path is None:
        errors.append(f"caller job {job_id}: with.{path_input_name} is required")
    elif _scalar_has_expression(literal_path):
        errors.append(f"caller job {job_id}: expressions are unsupported in with.{path_input_name}")
    elif literal_path != runtime_path:
        errors.append(f"caller job {job_id}: with.{path_input_name} does not match runtime input")
    return errors


def parse_date(value: str, field: str, errors: list[str]) -> date | None:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        errors.append(f"{field}: expected ISO date, got {value!r}")
        return None


def markdown(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def expand_repository(defaults: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(defaults)
    for key, value in item.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key].update(copy.deepcopy(value))
        else:
            result[key] = copy.deepcopy(value)
    return result


def expanded_repositories(data: dict[str, Any]) -> list[dict[str, Any]]:
    defaults = data.get("defaults", {})
    repositories = data.get("repositories", [])
    if not isinstance(defaults, dict) or not isinstance(repositories, list):
        return []
    return [expand_repository(defaults, item) for item in repositories if isinstance(item, dict)]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def validate_registry_data(data: dict[str, Any], *, today: date | None = None) -> list[str]:
    errors: list[str] = []
    today = today or date.today()
    if data.get("schema_version") != "opencoven.repository-registry/v1":
        errors.append("governance/repositories.json: unsupported schema_version")
    if data.get("organization") != "OpenCoven":
        errors.append("governance/repositories.json: organization must be OpenCoven")
    scope = data.get("scope", {})
    if scope.get("visibility") != "public-only":
        errors.append("registry scope must be public-only")
    if scope.get("private_inventory") != "federated-and-intentionally-omitted":
        errors.append("registry must explicitly omit private inventory")
    raw_repositories = data.get("repositories")
    if not isinstance(raw_repositories, list):
        return errors + ["registry repositories must be an array"]
    defaults = data.get("defaults")
    if not isinstance(defaults, dict):
        return errors + ["registry defaults must be an object"]
    repositories = expanded_repositories(data)
    if len(repositories) != len(raw_repositories):
        errors.append("registry repository entries must be objects")
    if scope.get("expected_public_repository_count") != len(raw_repositories):
        errors.append("registry expected_public_repository_count does not match repositories length")

    names: set[str] = set()
    domains: dict[str, str] = {}
    actual_order: list[str] = []
    allowed_lifecycle = {"incubating", "active", "maintenance", "deprecated", "archived", "tombstone"}
    allowed_canonicality = {"canonical", "supporting", "specimen", "historical", "none"}
    allowed_risk = {"R0", "R1", "R2", "R3", "R4"}
    destination_required = {
        "consolidate-then-retire",
        "evaluate-consolidation-or-private-incubation",
        "private-incubation-or-retire",
    }

    for index, item in enumerate(repositories):
        where = f"repositories[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{where}: expected object")
            continue
        name = item.get("name")
        actual_order.append(str(name))
        if not isinstance(name, str) or not name:
            errors.append(f"{where}.name: required")
            continue
        if name in names:
            errors.append(f"duplicate repository: {name}")
        names.add(name)
        if item.get("visibility") != "public":
            errors.append(f"{name}: public registry may contain only visibility=public")
        if item.get("lifecycle") not in allowed_lifecycle:
            errors.append(f"{name}: invalid lifecycle {item.get('lifecycle')!r}")
        if item.get("canonicality") not in allowed_canonicality:
            errors.append(f"{name}: invalid canonicality {item.get('canonicality')!r}")
        if item.get("risk_class") not in allowed_risk:
            errors.append(f"{name}: invalid risk class {item.get('risk_class')!r}")
        for field in ("owner", "technical_dri", "ownership_status", "purpose"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"{name}: {field} is required")
        observed = item.get("observed", {})
        if not isinstance(observed.get("default_branch"), str) or not observed.get("default_branch"):
            errors.append(f"{name}: observed.default_branch is required")
        if not isinstance(observed.get("archived"), bool):
            errors.append(f"{name}: observed.archived must be boolean")
        if item.get("lifecycle") == "archived" and observed.get("archived") is not True:
            errors.append(f"{name}: archived lifecycle requires observed.archived=true")
        if observed.get("archived") is True and item.get("lifecycle") != "archived":
            errors.append(f"{name}: observed archived repository must use archived lifecycle")

        canonical_domains = item.get("canonical_domains", [])
        if not isinstance(canonical_domains, list) or not all(isinstance(v, str) and v for v in canonical_domains):
            errors.append(f"{name}: canonical_domains must be non-empty strings")
            canonical_domains = []
        if item.get("canonicality") == "canonical" and not canonical_domains:
            errors.append(f"{name}: canonical repository must own at least one domain")
        if item.get("canonicality") != "canonical" and canonical_domains:
            errors.append(f"{name}: only canonical repositories may claim canonical_domains")
        for domain in canonical_domains:
            if domain in domains:
                errors.append(f"duplicate canonical domain {domain!r}: {domains[domain]} and {name}")
            else:
                domains[domain] = name

        disposition = item.get("disposition", {})
        if not isinstance(disposition, dict) or not disposition.get("state"):
            errors.append(f"{name}: disposition.state is required")
            disposition = {}
        if disposition.get("state") in destination_required and not disposition.get("destination"):
            errors.append(f"{name}: disposition {disposition.get('state')} requires destination")
        review_by = parse_date(disposition.get("review_by"), f"{name}.disposition.review_by", errors)
        if review_by and review_by < today and item.get("lifecycle") not in {"archived", "tombstone"}:
            errors.append(f"{name}: lifecycle/disposition review expired on {review_by.isoformat()}")

        manifest = item.get("agent_manifest", {})
        if manifest.get("status") not in {"enforced", "planned", "exempt"}:
            errors.append(f"{name}: invalid agent_manifest.status")
        if not isinstance(manifest.get("path"), str) or not manifest.get("path"):
            errors.append(f"{name}: agent_manifest.path is required")
        if manifest.get("status") == "exempt" and item.get("lifecycle") not in {"archived", "tombstone"}:
            errors.append(f"{name}: only archived/tombstone repositories may be manifest-exempt")
        if item.get("security_support") not in {"active", "limited", "unsupported", "historical"}:
            errors.append(f"{name}: invalid security_support")

    if actual_order != sorted(actual_order, key=str.lower):
        errors.append("registry repositories must be sorted by name")

    for item in repositories:
        destination = item.get("disposition", {}).get("destination")
        if not isinstance(destination, dict):
            continue
        if destination.get("kind") == "repository" and destination.get("name") not in names:
            errors.append(f"{item.get('name')}: destination repository {destination.get('name')!r} is not registered")
        if destination.get("kind") == "portfolio":
            for target in destination.get("names", []):
                if target not in names:
                    errors.append(f"{item.get('name')}: destination repository {target!r} is not registered")
        if destination.get("kind") == "private-overlay" and not destination.get("id"):
            errors.append(f"{item.get('name')}: private-overlay destination requires opaque id")

    return errors


def validate_manifest_data(data: dict[str, Any], *, registry_entry: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "opencoven.agent-repo/v1":
        errors.append("manifest: unsupported schema_version")
    repository = data.get("repository", {})
    risk = data.get("risk", {})
    agent = data.get("agent", {})
    contracts = data.get("contracts", {})
    required_repo = ("name", "lifecycle", "canonicality", "canonical_for", "does_not_own", "owner", "technical_dri", "ownership_status")
    for field in required_repo:
        if field not in repository:
            errors.append(f"manifest.repository.{field}: required")
    if risk.get("class") not in {"R0", "R1", "R2", "R3", "R4"}:
        errors.append("manifest.risk.class: invalid")
    for field in ("protected_paths", "generated_paths", "external_side_effects"):
        if not isinstance(risk.get(field), list):
            errors.append(f"manifest.risk.{field}: expected array")
    for field in ("network_policy", "secrets_policy"):
        if not isinstance(risk.get(field), str) or not risk.get(field):
            errors.append(f"manifest.risk.{field}: required")
    if not isinstance(agent.get("entrypoint"), str) or not agent.get("entrypoint"):
        errors.append("manifest.agent.entrypoint: required")
    if not isinstance(agent.get("bootstrap"), str) or not agent.get("bootstrap"):
        errors.append("manifest.agent.bootstrap: required")
    verify = agent.get("verify", {})
    for field in ("fast", "full"):
        if not isinstance(verify.get(field), str) or not verify.get(field):
            errors.append(f"manifest.agent.verify.{field}: required")
    for field in ("produces", "consumes"):
        if not isinstance(contracts.get(field), list):
            errors.append(f"manifest.contracts.{field}: expected array")

    canonical_for = repository.get("canonical_for", [])
    if repository.get("canonicality") == "canonical" and not canonical_for:
        errors.append("manifest: canonical repository must claim at least one domain")
    if repository.get("canonicality") != "canonical" and canonical_for:
        errors.append("manifest: noncanonical repository cannot claim canonical domains")

    if registry_entry:
        comparisons = {
            "repository.name": (repository.get("name"), registry_entry.get("name")),
            "repository.lifecycle": (repository.get("lifecycle"), registry_entry.get("lifecycle")),
            "repository.canonicality": (repository.get("canonicality"), registry_entry.get("canonicality")),
            "repository.canonical_for": (sorted(canonical_for), sorted(registry_entry.get("canonical_domains", []))),
            "repository.does_not_own": (
                sorted(repository.get("does_not_own", [])),
                sorted(registry_entry.get("does_not_own", [])),
            ),
            "repository.owner": (repository.get("owner"), registry_entry.get("owner")),
            "repository.technical_dri": (repository.get("technical_dri"), registry_entry.get("technical_dri")),
            "repository.ownership_status": (repository.get("ownership_status"), registry_entry.get("ownership_status")),
            "risk.class": (risk.get("class"), registry_entry.get("risk_class")),
        }
        for field, (actual, expected) in comparisons.items():
            if actual != expected:
                errors.append(f"manifest mismatch {field}: {actual!r} != registry {expected!r}")
    if risk.get("class") in {"R3", "R4"}:
        if not risk.get("protected_paths"):
            errors.append("manifest.risk.protected_paths: R3/R4 repositories require protected paths")
        expected_adapters = {
            "agent.bootstrap": agent.get("bootstrap") == "./scripts/agent-bootstrap",
            "agent.verify.fast": agent.get("verify", {}).get("fast") == "./scripts/agent-check fast",
            "agent.verify.full": agent.get("verify", {}).get("full") == "./scripts/agent-check full",
        }
        for field, ok in expected_adapters.items():
            if not ok:
                errors.append(f"manifest.{field}: R3/R4 repositories must use the canonical agent adapter")
    return errors


def validate_initiative_data(data: dict[str, Any], *, repository_names: set[str], decision_ids: set[str], today: date | None = None) -> list[str]:
    errors: list[str] = []
    today = today or date.today()
    if data.get("schema_version") != "opencoven.initiative/v1":
        errors.append("unsupported initiative schema_version")
    for field in ("id", "title", "status", "priority", "decision_owner", "technical_dri", "ownership_status", "outcome", "authority_boundary"):
        if not data.get(field):
            errors.append(f"initiative {data.get('id', '<unknown>')}: {field} required")
    for decision in data.get("decisions", []):
        if decision not in decision_ids:
            errors.append(f"initiative {data.get('id')}: unknown decision {decision}")
    for workstream in data.get("workstreams", []):
        repository = workstream.get("repository")
        if repository not in repository_names:
            errors.append(f"initiative {data.get('id')}: unregistered public workstream repository {repository!r}")
        if not workstream.get("responsibility"):
            errors.append(f"initiative {data.get('id')}: workstream responsibility required")
    criteria = data.get("exit_criteria", [])
    if not criteria:
        errors.append(f"initiative {data.get('id')}: exit_criteria required")
    if data.get("status") == "completed":
        for criterion in criteria:
            if criterion.get("state") != "met" or not criterion.get("evidence"):
                errors.append(f"initiative {data.get('id')}: completed criterion {criterion.get('id')} lacks met state and evidence")
    review_by = parse_date(data.get("review_by"), f"initiative {data.get('id')}.review_by", errors)
    if review_by and review_by < today and data.get("status") in {"proposed", "active", "verifying"}:
        errors.append(f"initiative {data.get('id')}: review expired on {review_by.isoformat()}")
    return errors


def validate_exception_data(data: dict[str, Any], *, control_ids: set[str], today: date | None = None) -> list[str]:
    errors: list[str] = []
    today = today or date.today()
    if data.get("schema_version") != "opencoven.exception-set/v1":
        errors.append("unsupported exception schema_version")
    seen: set[str] = set()
    for item in data.get("exceptions", []):
        ident = item.get("id")
        if not ident or ident in seen:
            errors.append(f"duplicate or missing exception id: {ident!r}")
        seen.add(ident)
        if item.get("control_id") not in control_ids:
            errors.append(f"exception {ident}: unknown control {item.get('control_id')!r}")
        created = parse_date(item.get("created"), f"exception {ident}.created", errors)
        expires = parse_date(item.get("expires"), f"exception {ident}.expires", errors)
        if created and expires and expires < created:
            errors.append(f"exception {ident}: expires before creation")
        if created and expires and (expires - created).days > 90:
            errors.append(f"exception {ident}: active window exceeds 90 days")
        if expires and expires < today and item.get("status") in {"proposed", "active"}:
            errors.append(f"exception {ident}: {item.get('status')} exception expired on {expires.isoformat()}")
    return errors
