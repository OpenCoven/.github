"""Repository model, cross-file validation, and deterministic generation."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from governance_core import (
    ACTION_USE, ROOT, SECRET_PATTERNS, SHA40, TEXT_SUFFIXES,
    expanded_repositories, load_json, markdown, sha256_text,
    resolve_trusted_target_file,
    validate_exception_data, validate_initiative_data,
    validate_manifest_data, validate_registry_data,
)

@dataclass
class Governance:
    root: Path = ROOT

    def path(self, value: str) -> Path:
        return self.root / value

    def registry(self) -> dict[str, Any]:
        return load_json(self.path("governance/repositories.json"))

    def registry_map(self) -> dict[str, dict[str, Any]]:
        return {item["name"]: item for item in expanded_repositories(self.registry())}

    def decision_index(self) -> dict[str, Any]:
        return load_json(self.path("decisions/index.json"))

    def initiative_files(self) -> list[Path]:
        return sorted(self.path("initiatives").glob("*.json"))

    def validate(self) -> list[str]:
        errors: list[str] = []
        required = [
            "README.md", "AGENTS.md", "LICENSE", "agent/manifest.json",
            "governance/repositories.json", "governance/lifecycle.json", "governance/controls.json", "governance/exceptions.json",
            "compatibility/dependencies.json", "compatibility/contracts.json", "compatibility/release-trains.json",
            "decisions/index.json", ".github/CODEOWNERS",
        ]
        for rel in required:
            if not self.path(rel).exists():
                errors.append(f"missing required path: {rel}")

        # Parse every JSON file and reject duplicate keys.
        for path in sorted(self.root.rglob("*.json")):
            try:
                load_json(path)
            except ValueError as exc:
                errors.append(str(exc))

        if errors:
            return errors

        registry = self.registry()
        errors.extend(validate_registry_data(registry))
        registry_map = {item["name"]: item for item in expanded_repositories(registry)}
        names = set(registry_map)

        manifest = load_json(self.path("agent/manifest.json"))
        errors.extend(validate_manifest_data(manifest, registry_entry=registry_map.get(".github")))
        entrypoint = manifest.get("agent", {}).get("entrypoint")
        if entrypoint and not self.path(entrypoint).exists():
            errors.append(f"manifest agent.entrypoint does not exist: {entrypoint}")

        decisions = self.decision_index()
        if decisions.get("schema_version") != "opencoven.decision-index/v1":
            errors.append("decisions/index.json: unsupported schema_version")
        decision_ids: set[str] = set()
        for item in decisions.get("decisions", []):
            ident = item.get("id")
            if ident in decision_ids:
                errors.append(f"duplicate decision id: {ident}")
            decision_ids.add(ident)
            path = self.path(item.get("path", ""))
            if not path.exists():
                errors.append(f"decision {ident}: missing path {item.get('path')}")
            elif f"# {ident}:" not in path.read_text(encoding="utf-8"):
                errors.append(f"decision {ident}: path heading does not match id")

        initiatives: dict[str, dict[str, Any]] = {}
        for path in self.initiative_files():
            data = load_json(path)
            ident = data.get("id")
            if ident in initiatives:
                errors.append(f"duplicate initiative id: {ident}")
            initiatives[ident] = data
            errors.extend(validate_initiative_data(data, repository_names=names, decision_ids=decision_ids))
        for ident, data in initiatives.items():
            for dependency in data.get("dependencies", []):
                if dependency not in initiatives:
                    errors.append(f"initiative {ident}: unknown dependency {dependency}")
        errors.extend(self._validate_initiative_cycles(initiatives))

        dependencies = load_json(self.path("compatibility/dependencies.json"))
        seen_edges: set[tuple[str, str, str]] = set()
        for edge in dependencies.get("edges", []):
            key = (edge.get("producer"), edge.get("consumer"), edge.get("relationship"))
            if key in seen_edges:
                errors.append(f"duplicate dependency edge: {key}")
            seen_edges.add(key)
            if edge.get("producer") not in names or edge.get("consumer") not in names:
                errors.append(f"dependency references unregistered public repository: {key}")
            if edge.get("producer") == edge.get("consumer"):
                errors.append(f"self dependency is not allowed: {key}")
            if not edge.get("required_evidence"):
                errors.append(f"dependency lacks required_evidence: {key}")

        contracts = load_json(self.path("compatibility/contracts.json"))
        contract_ids: set[str] = set()
        for contract in contracts.get("contracts", []):
            if contract.get("id") in contract_ids:
                errors.append(f"duplicate contract id: {contract.get('id')}")
            contract_ids.add(contract.get("id"))
            if contract.get("owner") not in names:
                errors.append(f"contract {contract.get('id')}: unregistered owner {contract.get('owner')}")

        release_trains = load_json(self.path("compatibility/release-trains.json"))
        for train in release_trains.get("release_trains", []):
            for member in train.get("members", []):
                if member not in names:
                    errors.append(f"release train {train.get('id')}: unregistered member {member}")

        controls = load_json(self.path("governance/controls.json"))
        control_ids: set[str] = set()
        for control in controls.get("controls", []):
            ident = control.get("id")
            if ident in control_ids:
                errors.append(f"duplicate control id: {ident}")
            control_ids.add(ident)
            for evidence in control.get("evidence", []):
                if evidence.startswith("OpenCoven/"):
                    continue
                local = self.path(evidence)
                if not local.exists():
                    errors.append(f"control {ident}: evidence path does not exist: {evidence}")

        exceptions = load_json(self.path("governance/exceptions.json"))
        errors.extend(validate_exception_data(exceptions, control_ids=control_ids))
        errors.extend(self.validate_workflows())
        errors.extend(self.scan_secrets())
        errors.extend(self.validate_generated())
        return sorted(set(errors))

    @staticmethod
    def _validate_initiative_cycles(initiatives: dict[str, dict[str, Any]]) -> list[str]:
        errors: list[str] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str, stack: list[str]) -> None:
            if node in visiting:
                cycle = " -> ".join(stack + [node])
                errors.append(f"initiative dependency cycle: {cycle}")
                return
            if node in visited or node not in initiatives:
                return
            visiting.add(node)
            for dep in initiatives[node].get("dependencies", []):
                visit(dep, stack + [node])
            visiting.remove(node)
            visited.add(node)

        for ident in initiatives:
            visit(ident, [])
        return errors

    def validate_workflows(self) -> list[str]:
        errors: list[str] = []
        workflow_dir = self.path(".github/workflows")
        for path in sorted(list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))):
            rel = path.relative_to(self.root)
            text = path.read_text(encoding="utf-8")
            if not re.search(r"(?m)^permissions:\s*$", text):
                errors.append(f"{rel}: top-level permissions block required")
            if "pull_request_target:" in text:
                errors.append(f"{rel}: pull_request_target is forbidden")
            for action in ACTION_USE.findall(text):
                if action.startswith("./") or action.startswith("docker://"):
                    continue
                if "@" not in action:
                    errors.append(f"{rel}: action without immutable ref: {action}")
                    continue
                _, ref = action.rsplit("@", 1)
                if not SHA40.fullmatch(ref):
                    errors.append(f"{rel}: action ref must be a full commit SHA: {action}")
            if (
                re.search(r"(?m)^\s{0,4}pull_request:\s*(?:$|#|{|null\s*$|~\s*$)", text)
                or re.search(r"(?m)^on:\s*pull_request\s*$", text)
                or re.search(r"(?m)^on:\s*\[.*\bpull_request\b.*\]\s*$", text)
                or re.search(r"(?m)^on:\s*{\s*pull_request\s*:", text)
                or re.search(r"(?m)^on:\s*{[^{}\n]*,\s*pull_request\s*:", text)
            ):
                permission_section = self._top_level_block(text, "permissions")
                if re.search(r"(?m)^\s+[A-Za-z-]+:\s*write\s*$", permission_section):
                    errors.append(f"{rel}: pull_request workflow may not request write permission")
        return errors

    @staticmethod
    def _top_level_block(text: str, key: str) -> str:
        lines = text.splitlines()
        start = None
        result: list[str] = []
        for index, line in enumerate(lines):
            if line == f"{key}:":
                start = index + 1
                continue
            if start is not None:
                if line and not line.startswith((" ", "\t", "#")):
                    break
                result.append(line)
        return "\n".join(result)

    def scan_secrets(self) -> list[str]:
        errors: list[str] = []
        ignored = {"generated/portfolio.md"}  # generated content still derives from validated public input
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or ".git" in path.parts or path.suffix not in TEXT_SUFFIXES:
                continue
            rel = str(path.relative_to(self.root))
            if rel in ignored:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(text):
                    errors.append(f"{rel}: possible {label} material")
        return errors

    def generated_content(self) -> dict[str, str]:
        registry = expanded_repositories(self.registry())
        dependencies = load_json(self.path("compatibility/dependencies.json"))["edges"]
        controls = load_json(self.path("governance/controls.json"))["controls"]
        initiatives = [load_json(path) for path in self.initiative_files()]

        counts = defaultdict(int)
        for item in registry:
            counts[item["lifecycle"]] += 1
        portfolio = [
            "# Generated public repository portfolio",
            "",
            "> Generated by `python3 scripts/governance.py generate`. Do not edit by hand.",
            "",
            f"Registry digest: `{sha256_text(json.dumps(self.registry(), sort_keys=True, separators=(',', ':')))}`",
            "",
            "## Summary",
            "",
            "| Lifecycle | Count |",
            "|---|---:|",
        ]
        for state in ("active", "incubating", "maintenance", "deprecated", "archived", "tombstone"):
            portfolio.append(f"| {state} | {counts[state]} |")
        portfolio += ["", "## Repositories", "", "| Repository | Lifecycle | Canonicality | Risk | Owner | Disposition | Manifest |", "|---|---|---|---:|---|---|---|"]
        for item in registry:
            portfolio.append("| {name} | {lifecycle} | {canonicality} | {risk_class} | @{owner} | {state} | {manifest} |".format(
                **item,
                state=markdown(item["disposition"]["state"]),
                manifest=item["agent_manifest"]["status"],
            ))
        portfolio += ["", "This is a public-only view. Private repository inventory is intentionally federated and omitted.", ""]

        ownership = [
            "# Generated canonical public ownership map", "",
            "> Generated from `governance/repositories.json`. A governance claim identifies ownership; it does not grant protected runtime authority.", "",
            "| Canonical domain | Repository | Technical DRI | Risk |", "|---|---|---|---:|",
        ]
        owned: list[tuple[str, dict[str, Any]]] = []
        for item in registry:
            for domain in item["canonical_domains"]:
                owned.append((domain, item))
        for domain, item in sorted(owned):
            ownership.append(f"| `{domain}` | `{item['name']}` | @{item['technical_dri']} | {item['risk_class']} |")
        ownership.append("")

        graph = [
            "%% Generated by scripts/governance.py; do not edit.",
            "flowchart LR",
        ]
        for item in registry:
            safe = re.sub(r"[^A-Za-z0-9_]", "_", item["name"])
            graph.append(f'  {safe}["{item["name"]}"]')
        for edge in dependencies:
            source = re.sub(r"[^A-Za-z0-9_]", "_", edge["producer"])
            target = re.sub(r"[^A-Za-z0-9_]", "_", edge["consumer"])
            label = edge["relationship"].replace('"', "'")
            graph.append(f'  {source} -->|"{label}"| {target}')
        graph.append("")

        initiative_view = [
            "# Generated cross-repository initiatives", "",
            "> Generated from `initiatives/*.json`. Implementation status remains authoritative in linked owning-repository evidence.", "",
            "| Initiative | Priority | Status | Decision owner | Technical DRI | Review by | Open criteria |", "|---|---:|---|---|---|---|---:|",
        ]
        for item in sorted(initiatives, key=lambda value: (value["priority"], value["id"])):
            open_count = sum(1 for criterion in item["exit_criteria"] if criterion["state"] != "met")
            initiative_view.append(f"| `{item['id']}` | {item['priority']} | {item['status']} | @{item['decision_owner']} | @{item['technical_dri']} | {item['review_by']} | {open_count} |")
        initiative_view.append("")

        control_view = [
            "# Generated governance control index", "",
            "> Generated from `governance/controls.json`. A control marked specified or implemented is not necessarily administratively applied or operationally effective.", "",
            "| Control | Objective | Enforcement | State |", "|---|---|---|---|",
        ]
        for item in controls:
            control_view.append(f"| `{item['id']}` {markdown(item['title'])} | {markdown(item['objective'])} | {markdown(item['enforcement'])} | {markdown(item['status'])} |")
        control_view.append("")

        return {
            "generated/portfolio.md": "\n".join(portfolio),
            "generated/ownership.md": "\n".join(ownership),
            "generated/dependencies.mmd": "\n".join(graph),
            "generated/initiatives.md": "\n".join(initiative_view),
            "generated/controls.md": "\n".join(control_view),
        }

    def generate(self) -> None:
        for rel, content in self.generated_content().items():
            path = self.path(rel)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    def validate_generated(self) -> list[str]:
        errors: list[str] = []
        for rel, expected in self.generated_content().items():
            path = self.path(rel)
            if not path.exists():
                errors.append(f"missing generated file: {rel}")
                continue
            actual = path.read_text(encoding="utf-8")
            if actual != expected:
                errors.append(f"stale generated file: {rel}; run python3 scripts/governance.py generate")
        return errors

    def validate_manifest_file(
        self,
        target_root: Path,
        manifest_path: str,
        *,
        caller_repository: str | None = None,
        allow_self_declared_repository: bool = False,
    ) -> list[str]:
        try:
            trusted_path = resolve_trusted_target_file(target_root, manifest_path, label="manifest")
            data = load_json(trusted_path)
        except ValueError as exc:
            return [str(exc)]
        errors: list[str] = []
        repository = data.get("repository", {})
        if caller_repository:
            if not caller_repository.startswith("OpenCoven/") or caller_repository.count("/") != 1:
                errors.append(f"caller repository must be an OpenCoven owner/repo name: {caller_repository!r}")
                repo_name = ""
            else:
                repo_name = caller_repository.split("/", 1)[1]
        elif allow_self_declared_repository:
            declared_name = repository.get("name", "")
            if not isinstance(declared_name, str):
                errors.append("manifest repository.name must be a string")
                repo_name = ""
            else:
                repo_name = declared_name
        else:
            return ["caller repository is required unless local self-declared mode is explicitly enabled"]
        if repo_name and repository.get("name") != repo_name:
            errors.append(f"manifest repository.name {repository.get('name')!r} does not match caller repository {repo_name!r}")
        entry = self.registry_map().get(repo_name)
        if not entry:
            errors.append(f"caller repository is not registered in the public registry: {repo_name!r}")
        else:
            manifest_record = entry.get("agent_manifest", {})
            if manifest_record.get("path") != manifest_path:
                errors.append(
                    f"manifest path {manifest_path!r} does not match registry agent_manifest.path "
                    f"{manifest_record.get('path')!r}"
                )
        errors.extend(validate_manifest_data(data, registry_entry=entry))
        return sorted(set(errors))

    def validate_evidence_file(self, target_root: Path, evidence_path: str) -> list[str]:
        try:
            trusted_path = resolve_trusted_target_file(
                target_root,
                evidence_path,
                label="evidence",
                required_prefix="evidence",
                required_suffixes=(".json",),
            )
            data = load_json(trusted_path)
        except ValueError as exc:
            return [str(exc)]
        errors: list[str] = []
        if not isinstance(data, dict):
            return ["evidence packet must be a JSON object"]

        def _require_non_empty_string(value: Any, label: str) -> None:
            if not isinstance(value, str) or not value:
                errors.append(f"{label} must be a non-empty string")

        def _require_string_array(value: Any, label: str, *, min_items: int = 0) -> list[str]:
            if not isinstance(value, list):
                errors.append(f"{label} must be an array")
                return []
            if len(value) < min_items:
                errors.append(f"{label} must contain at least {min_items} item(s)")
            values: list[str] = []
            for index, item in enumerate(value):
                if not isinstance(item, str) or not item:
                    errors.append(f"{label}[{index}] must be a non-empty string")
                    continue
                values.append(item)
            return values

        if data.get("schema_version") != "opencoven.governance-evidence/v1":
            errors.append("evidence: unsupported schema_version")
        change = data.get("change")
        if not isinstance(change, dict):
            errors.append("evidence.change must be an object")
        else:
            _require_non_empty_string(change.get("objective"), "evidence.change.objective")
            _require_string_array(change.get("acceptance_criteria"), "evidence.change.acceptance_criteria", min_items=1)
            _require_string_array(change.get("non_goals"), "evidence.change.non_goals")
        authority = data.get("authority")
        if not isinstance(authority, dict):
            errors.append("evidence.authority must be an object")
            authority = {}
        if authority.get("authorization_effect") != "none-metadata-only":
            errors.append("evidence.authority.authorization_effect must be none-metadata-only")
        if authority.get("risk_class") not in {"R0", "R1", "R2", "R3", "R4"}:
            errors.append("evidence.authority.risk_class invalid")
        _require_string_array(authority.get("protected_boundaries"), "evidence.authority.protected_boundaries")
        sources = data.get("sources")
        if not isinstance(sources, list):
            errors.append("evidence.sources must be an array")
            sources = []
        if not sources:
            errors.append("evidence.sources requires at least one exact source")
        for index, source in enumerate(sources):
            if not isinstance(source, dict):
                errors.append(f"evidence.sources[{index}] must be an object")
                continue
            _require_non_empty_string(source.get("kind"), f"evidence.sources[{index}].kind")
            _require_non_empty_string(source.get("reference"), f"evidence.sources[{index}].reference")
            _require_non_empty_string(source.get("revision"), f"evidence.sources[{index}].revision")
        _require_string_array(data.get("files"), "evidence.files")
        verification = data.get("verification")
        if not isinstance(verification, list):
            errors.append("evidence.verification must be an array")
            verification = []
        if not verification:
            errors.append("evidence.verification requires at least one result")
        for index, result in enumerate(verification):
            if not isinstance(result, dict):
                errors.append(f"evidence.verification[{index}] must be an object")
                continue
            _require_non_empty_string(result.get("command"), f"evidence.verification[{index}].command")
            _require_non_empty_string(result.get("environment"), f"evidence.verification[{index}].environment")
            if result.get("result") not in {"pass", "fail", "skipped", "unsupported"}:
                errors.append(f"evidence.verification[{index}].result invalid")
            if "evidence" in result and not isinstance(result.get("evidence"), str):
                errors.append(f"evidence.verification[{index}].evidence must be a string")
        _require_non_empty_string(data.get("migration"), "evidence.migration")
        _require_non_empty_string(data.get("rollback"), "evidence.rollback")
        _require_string_array(data.get("uncertainty"), "evidence.uncertainty")
        return errors
