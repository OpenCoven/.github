from __future__ import annotations

import argparse
import copy
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import textwrap
import unittest
import sys
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "governance.py"
SPEC = importlib.util.spec_from_file_location("opencoven_governance", MODULE_PATH)
assert SPEC and SPEC.loader
GOV = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GOV
SPEC.loader.exec_module(GOV)
ROOT = Path(__file__).resolve().parents[1]

# governance.py inserts scripts/ onto sys.path as a side effect of module
# execution above, so governance_cli is importable directly here in order to
# patch its module-global `github_request` used internally by upsert_drift_issue.
import governance_cli  # noqa: E402


class RegistryInvariantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads((ROOT / "governance/repositories.json").read_text())

    def test_current_registry_is_valid_at_snapshot_date(self) -> None:
        self.assertEqual([], GOV.validate_registry_data(self.registry, today=date(2026, 9, 3)))

    def test_duplicate_canonical_domain_fails_closed(self) -> None:
        data = copy.deepcopy(self.registry)
        data["repositories"][1]["canonicality"] = "canonical"
        data["repositories"][1]["canonical_domains"] = ["organization.governance"]
        errors = GOV.validate_registry_data(data, today=date(2026, 9, 3))
        self.assertTrue(any("duplicate canonical domain" in error for error in errors), errors)

    def test_private_repository_in_public_registry_is_rejected(self) -> None:
        data = copy.deepcopy(self.registry)
        data["repositories"][0]["visibility"] = "private"
        errors = GOV.validate_registry_data(data, today=date(2026, 9, 3))
        self.assertTrue(any("only visibility=public" in error for error in errors), errors)

    def test_archived_metadata_must_match_lifecycle(self) -> None:
        data = copy.deepcopy(self.registry)
        target = next(item for item in data["repositories"] if item["name"] == "cast-codes")
        target["observed"]["archived"] = False
        errors = GOV.validate_registry_data(data, today=date(2026, 9, 3))
        self.assertTrue(any("archived lifecycle" in error for error in errors), errors)

    def test_expired_review_is_detected(self) -> None:
        data = copy.deepcopy(self.registry)
        data["repositories"][0]["disposition"] = {"state": "retain", "review_by": "2026-09-02"}
        errors = GOV.validate_registry_data(data, today=date(2026, 9, 3))
        self.assertTrue(any("review expired" in error for error in errors), errors)

    def test_unavailable_public_record_is_explicitly_unresolved(self) -> None:
        target = next(
            item
            for item in self.registry["repositories"]
            if item["name"] == "opencoven-beta-august-hackathon-2026"
        )
        self.assertEqual("unavailable-needs-owner-evidence", target.get("observation_status"))


class OwnershipBoundaryTests(unittest.TestCase):
    """Regression coverage for the Psyche/Coven ownership boundary.

    These assert exact canonical owners and reciprocal disclaims by name
    rather than relying on the registry's exact-string duplicate check,
    which cannot detect conceptually overlapping domains that use
    different literal strings (for example Psyche's project-orchestration
    leases/retries/recovery/receipts versus Coven's automation-lifecycle
    leases/retries/recovery/receipts).
    """

    PROJECT_ORCHESTRATION_DOMAINS = {
        "project-orchestration.tasks",
        "project-orchestration.lanes",
        "project-orchestration.leases",
        "project-orchestration.approvals",
        "project-orchestration.receipts",
        "project-orchestration.retries",
        "project-orchestration.recovery",
    }

    AUTOMATION_LIFECYCLE_DOMAINS = {
        "automation.definitions",
        "automation.revisions",
        "automation.schedule-planning",
        "automation.occurrences",
        "automation.runs",
        "automation.attempts",
        "automation.leases",
        "automation.fences",
        "automation.retries",
        "automation.recovery",
        "automation.events",
        "automation.changefeed",
        "automation.artifacts",
        "automation.receipts",
    }

    def setUp(self) -> None:
        self.registry = json.loads((ROOT / "governance/repositories.json").read_text())
        self.repos = {item["name"]: item for item in self.registry["repositories"]}

    def test_psyche_owns_exact_project_orchestration_domains(self) -> None:
        psyche = self.repos["psyche"]
        self.assertEqual(set(psyche["canonical_domains"]), self.PROJECT_ORCHESTRATION_DOMAINS)

    def test_coven_owns_exact_automation_lifecycle_domains(self) -> None:
        coven = self.repos["coven"]
        self.assertTrue(
            self.AUTOMATION_LIFECYCLE_DOMAINS.issubset(set(coven["canonical_domains"])),
            coven["canonical_domains"],
        )

    def test_psyche_disclaims_coven_automation_lifecycle(self) -> None:
        psyche = self.repos["psyche"]
        self.assertIn("automation.lifecycle", psyche["does_not_own"])

    def test_coven_disclaims_project_orchestration(self) -> None:
        coven = self.repos["coven"]
        self.assertIn("project-orchestration", coven["does_not_own"])

    def test_no_repository_other_than_psyche_claims_project_orchestration_domains(self) -> None:
        for item in self.registry["repositories"]:
            if item["name"] == "psyche":
                continue
            claimed = set(item.get("canonical_domains", [])) & self.PROJECT_ORCHESTRATION_DOMAINS
            self.assertFalse(claimed, f"{item['name']} unexpectedly claims {claimed}")

    def test_no_repository_other_than_coven_claims_automation_lifecycle_domains(self) -> None:
        for item in self.registry["repositories"]:
            if item["name"] == "coven":
                continue
            claimed = set(item.get("canonical_domains", [])) & self.AUTOMATION_LIFECYCLE_DOMAINS
            self.assertFalse(claimed, f"{item['name']} unexpectedly claims {claimed}")

    def test_psyche_and_coven_canonical_domains_are_disjoint(self) -> None:
        psyche_domains = set(self.repos["psyche"]["canonical_domains"])
        coven_domains = set(self.repos["coven"]["canonical_domains"])
        self.assertTrue(psyche_domains.isdisjoint(coven_domains), psyche_domains & coven_domains)

    def test_identity_and_authorization_semantics_stay_with_their_canonical_owners(self) -> None:
        familiar_contract = self.repos["familiar-contract"]
        coven_threads = self.repos["coven-threads"]
        coven = self.repos["coven"]
        self.assertTrue(any(domain.startswith("identity.") for domain in familiar_contract["canonical_domains"]))
        self.assertTrue(any(domain.startswith("authority.") for domain in coven_threads["canonical_domains"]))
        self.assertIn("familiar.identity", coven["does_not_own"])
        self.assertIn("protected.authorization", coven["does_not_own"])


class InitiativeInvariantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry_names = {
            item["name"]
            for item in json.loads((ROOT / "governance/repositories.json").read_text())["repositories"]
        }
        self.decisions = {
            item["id"]
            for item in json.loads((ROOT / "decisions/index.json").read_text())["decisions"]
        }
        self.initiative = json.loads((ROOT / "initiatives/organization-governance-plane-v1.json").read_text())

    def test_completed_initiative_requires_exact_evidence(self) -> None:
        data = copy.deepcopy(self.initiative)
        data["status"] = "completed"
        errors = GOV.validate_initiative_data(
            data,
            repository_names=self.registry_names,
            decision_ids=self.decisions,
            today=date(2026, 9, 3),
        )
        self.assertTrue(any("lacks met state and evidence" in error for error in errors), errors)

    def test_unregistered_public_workstream_is_rejected(self) -> None:
        data = copy.deepcopy(self.initiative)
        data["workstreams"][0]["repository"] = "not-a-public-repository"
        errors = GOV.validate_initiative_data(
            data,
            repository_names=self.registry_names,
            decision_ids=self.decisions,
            today=date(2026, 9, 3),
        )
        self.assertTrue(any("unregistered public workstream" in error for error in errors), errors)


class ExceptionInvariantTests(unittest.TestCase):
    def test_active_expired_exception_is_rejected(self) -> None:
        data = {
            "schema_version": "opencoven.exception-set/v1",
            "exceptions": [{
                "id": "EX-001",
                "control_id": "GOV-001",
                "scope": "test",
                "owner": "BunsDev",
                "approver": "BunsDev",
                "rationale": "test",
                "risk": "test",
                "compensating_controls": ["test"],
                "created": "2026-08-01",
                "expires": "2026-09-01",
                "status": "active",
                "remediation": "test",
            }],
        }
        errors = GOV.validate_exception_data(data, control_ids={"GOV-001"}, today=date(2026, 9, 3))
        self.assertTrue(any("expired" in error for error in errors), errors)


class WorkflowInvariantTests(unittest.TestCase):
    def test_mutable_action_tag_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / ".github/workflows/test.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "name: test\non: push\npermissions:\n  contents: read\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n"
            )
            errors = GOV.Governance(root).validate_workflows()
            self.assertTrue(any("full commit SHA" in error for error in errors), errors)

    def test_pinned_action_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / ".github/workflows/test.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "name: test\non: push\npermissions:\n  contents: read\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n"
            )
            self.assertEqual([], GOV.Governance(root).validate_workflows())

    def test_mutable_docker_action_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / ".github/workflows/test.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "name: test\non: push\npermissions:\n  contents: read\njobs:\n  test:\n"
                "    runs-on: ubuntu-latest\n    steps:\n"
                "      - uses: docker://attacker/image:latest\n"
            )
            errors = GOV.Governance(root).validate_workflows()
            self.assertTrue(any("Docker action must use an immutable digest" in error for error in errors), errors)

    def test_flow_style_action_use_is_rejected_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / ".github/workflows/test.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "name: test\non: push\npermissions:\n  contents: read\njobs:\n  test:\n"
                "    runs-on: ubuntu-latest\n    steps:\n"
                "      - { uses: attacker/action@main }\n"
            )
            errors = GOV.Governance(root).validate_workflows()
            self.assertTrue(any("flow-style action mappings are unsupported" in error for error in errors), errors)

    def test_flow_sequence_action_use_is_rejected_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / ".github/workflows/test.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "name: test\non: push\npermissions:\n  contents: read\njobs:\n  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps: [{ uses: attacker/action@main }]\n"
            )
            errors = GOV.Governance(root).validate_workflows()
            self.assertTrue(any("flow-style action mappings are unsupported" in error for error in errors), errors)

    def test_pull_request_job_level_write_permission_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / ".github/workflows/test.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "name: test\non: pull_request\npermissions:\n  contents: read\njobs:\n  mutate:\n"
                "    permissions:\n      contents: write\n      id-token: write\n"
                "    runs-on: ubuntu-latest\n    steps:\n"
                "      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n"
            )
            errors = GOV.Governance(root).validate_workflows()
            self.assertTrue(any("job-level write permission" in error for error in errors), errors)

    def test_pull_request_job_level_permission_variants_are_rejected(self) -> None:
        variants = (
            "    permissions: { contents: write }\n",
            "    permissions:  # job grant\n      contents: write\n",
        )
        for permissions in variants:
            with self.subTest(permissions=permissions), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                workflow = root / ".github/workflows/test.yml"
                workflow.parent.mkdir(parents=True)
                workflow.write_text(
                    "name: test\non: pull_request\npermissions:\n  contents: read\njobs:\n  mutate:\n"
                    f"{permissions}"
                    "    runs-on: ubuntu-latest\n    steps:\n"
                    "      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n"
                )
                errors = GOV.Governance(root).validate_workflows()
                self.assertTrue(any("job-level write permission" in error for error in errors), errors)

    def test_pull_request_inline_mapping_is_treated_as_pr_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / ".github/workflows/test.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "name: test\n"
                "on:\n"
                "  pull_request: { branches: [main] }\n"
                "permissions:\n"
                "  contents: read\n"
                "  pull-requests: write\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n"
            )
            errors = GOV.Governance(root).validate_workflows()
            self.assertTrue(any("pull_request workflow may not request write permission" in error for error in errors), errors)

    def test_pull_request_flow_mapping_is_treated_as_pr_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / ".github/workflows/test.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "name: test\n"
                "on: { pull_request: { branches: [main] } }\n"
                "permissions:\n"
                "  contents: read\n"
                "  pull-requests: write\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n"
            )
            errors = GOV.Governance(root).validate_workflows()
            self.assertTrue(any("pull_request workflow may not request write permission" in error for error in errors), errors)

    def test_non_pr_flow_mapping_does_not_trigger_pr_write_restriction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / ".github/workflows/test.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                "name: test\n"
                "on: { workflow_run: { workflows: [pull_request] } }\n"
                "permissions:\n"
                "  contents: read\n"
                "  pull-requests: write\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n"
            )
            errors = GOV.Governance(root).validate_workflows()
            self.assertFalse(any("pull_request workflow may not request write permission" in error for error in errors), errors)

    def test_reusable_workflows_do_not_interpolate_path_inputs_in_shell(self) -> None:
        for workflow_name, input_name in (
            ("reusable-agent-readiness.yml", "manifest_path"),
            ("reusable-evidence-packet.yml", "evidence_path"),
        ):
            with self.subTest(workflow=workflow_name):
                text = (ROOT / ".github/workflows" / workflow_name).read_text()
                self.assertNotIn(f'target/${{{{ inputs.{input_name} }}}}', text)
                self.assertNotIn(f'"$GITHUB_WORKSPACE/target/${{{{ inputs.{input_name} }}}}"', text)
                self.assertIn(f"{input_name.upper()}: ${{{{ inputs.{input_name} }}}}", text)
                self.assertIn(f'"${input_name.upper()}"', text)

    def test_inline_preflights_do_not_trigger_actions_expression_evaluation(self) -> None:
        for workflow_name in (
            "reusable-agent-readiness.yml",
            "reusable-evidence-packet.yml",
        ):
            with self.subTest(workflow=workflow_name):
                script = _extract_inline_preflight_script(workflow_name)
                self.assertNotIn("${{", script, "Actions evaluates run bodies before Python")


SHA_A = "a" * 40
SHA_B = "b" * 40


def _minimal_registry(repo: str = "coven-code", *, risk: str = "R3") -> dict:
    return {
        "$schema": "../schemas/repository-registry.schema.json",
        "schema_version": "opencoven.repository-registry/v1",
        "organization": "OpenCoven",
        "scope": {
            "visibility": "public-only",
            "observed_as_of": "2026-09-05",
            "expected_public_repository_count": 1,
            "private_inventory": "federated-and-intentionally-omitted",
        },
        "defaults": {
            "visibility": "public",
            "observed": {"default_branch": "main", "archived": False},
            "owner": "BunsDev",
            "technical_dri": "BunsDev",
            "ownership_status": "bootstrap-single-owner",
            "canonical_domains": [],
            "does_not_own": ["runtime.persistence"],
            "disposition": {"state": "retain", "review_by": "2026-12-02"},
            "agent_manifest": {"status": "enforced", "path": "agent/manifest.json"},
            "security_support": "active",
        },
        "repositories": [{
            "name": repo,
            "lifecycle": "active",
            "canonicality": "supporting",
            "risk_class": risk,
            "purpose": "Synthetic public repository fixture.",
        }],
    }


def _minimal_manifest(repo: str = "coven-code", *, risk: str = "R3") -> dict:
    return {
        "$schema": "../schemas/agent-manifest.schema.json",
        "schema_version": "opencoven.agent-repo/v1",
        "repository": {
            "name": repo,
            "lifecycle": "active",
            "canonicality": "supporting",
            "canonical_for": [],
            "does_not_own": ["runtime.persistence"],
            "owner": "BunsDev",
            "technical_dri": "BunsDev",
            "ownership_status": "bootstrap-single-owner",
        },
        "risk": {
            "class": risk,
            "protected_paths": ["src/**"],
            "generated_paths": ["generated/**"],
            "network_policy": "deny-by-default",
            "secrets_policy": "forbidden-in-repository",
            "external_side_effects": [],
        },
        "agent": {
            "entrypoint": "AGENTS.md",
            "bootstrap": "./scripts/agent-bootstrap",
            "verify": {
                "fast": "./scripts/agent-check fast",
                "full": "./scripts/agent-check full",
            },
        },
        "contracts": {"produces": [], "consumes": []},
    }


def _minimal_evidence() -> dict:
    return {
        "$schema": "../schemas/evidence-packet.schema.json",
        "schema_version": "opencoven.governance-evidence/v1",
        "change": {"objective": "test", "acceptance_criteria": ["test"], "non_goals": []},
        "authority": {
            "risk_class": "R3",
            "authorization_effect": "none-metadata-only",
            "protected_boundaries": [],
        },
        "sources": [{"kind": "test", "reference": "test", "revision": "test"}],
        "files": ["README.md"],
        "verification": [{"command": "test", "result": "pass", "environment": "test"}],
        "migration": "test",
        "rollback": "test",
        "uncertainty": [],
    }


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _caller_workflow(*, reusable: str = "reusable-agent-readiness.yml", uses_ref: str = SHA_A,
                     policy_ref: str = SHA_A, path_input: str | None = "agent/manifest.json",
                     path_input_name: str = "manifest_path", extra_job: str = "",
                     on_block: str = "on:\n  pull_request:\n") -> str:
    with_block = f"      policy_ref: {policy_ref}\n"
    if path_input is not None:
        with_block += f"      {path_input_name}: {path_input}\n"
    return (
        "name: caller\n"
        f"{on_block}"
        "permissions:\n"
        "  contents: read\n"
        "jobs:\n"
        "  readiness:\n"
        "    permissions:\n"
        "      contents: read\n"
        f"    uses: OpenCoven/.github/.github/workflows/{reusable}@{uses_ref}\n"
        "    with:\n"
        f"{with_block}"
        f"{extra_job}"
    )


def _decoy_caller_workflow(*, reusable: str, path_input_name: str, path_input: str) -> str:
    return (
        "name: caller\n"
        "on: pull_request\n"
        "permissions:\n"
        "  contents: read\n"
        "jobs:\n"
        "  actual:\n"
        f"    uses: OpenCoven/.github/.github/workflows/{reusable}@{SHA_A}\n"
        "    with:\n"
        f"      policy_ref: {SHA_B}\n"
        f"      {path_input_name}: {path_input}\n"
        "  decoy:\n"
        "    if: false\n"
        f"    uses: OpenCoven/.github/.github/workflows/{reusable}@{SHA_B}\n"
        f"    with: {{ policy_ref: {SHA_B}, {path_input_name}: {path_input} }}\n"
    )


def _ambiguous_actual_uses_with_decoy(*, reusable: str, path_input_name: str, path_input: str,
                                      actual_uses: str) -> str:
    return (
        "name: caller\n"
        "on: pull_request\n"
        "permissions:\n"
        "  contents: read\n"
        "jobs:\n"
        "  actual:\n"
        f"{actual_uses}"
        "    with:\n"
        f"      policy_ref: {SHA_A}\n"
        f"      {path_input_name}: {path_input}\n"
        "  decoy:\n"
        "    if: false\n"
        f"    uses: OpenCoven/.github/.github/workflows/{reusable}@{SHA_A}\n"
        "    with:\n"
        f"      policy_ref: {SHA_A}\n"
        f"      {path_input_name}: {path_input}\n"
    )


def _extract_inline_preflight_script(workflow_name: str) -> str:
    text = (ROOT / ".github/workflows" / workflow_name).read_text(encoding="utf-8")
    marker = "Preflight caller policy binding before policy checkout"
    start = text.index(marker)
    match = re.search(r"python3 - <<'PY'\n(?P<body>.*?)\n\s+PY", text[start:], re.DOTALL)
    if not match:
        raise AssertionError(f"preflight script not found in {workflow_name}")
    return textwrap.dedent(match.group("body"))


SUPPORTED_EVENT_ON_BLOCKS = {
    "plain-scalar": "on: push\n",
    "double-quoted-scalar": 'on: "pull_request"\n',
    "single-quoted-scalar": "on: 'workflow_dispatch'\n",
    "mapping": "on:\n  pull_request:\n",
    "mapping-null": "on:\n  push: null\n",
    "mapping-with-options": "on:\n  pull_request:\n    branches: [main]\n",
    "block-sequence": "on:\n  - push\n  - workflow_dispatch\n",
    "flow-sequence": 'on: [push, "pull_request", \'workflow_dispatch\']\n',
}


UNSUPPORTED_EVENT_ON_BLOCKS = {
    "pull-request-target-scalar": "on: pull_request_target\n",
    "pull-request-target-mapping": "on:\n  pull_request_target:\n",
    "pull-request-target-flow-sequence": "on: [push, pull_request_target]\n",
    "quoted-top-level-on-key": '"on":\n  pull_request:\n',
    "folded-scalar-strip": "on: >-\n  workflow_call\n",
    "folded-scalar-keep": "on: >+\n  workflow_call\n",
    "folded-scalar-indent": "on: >2\n  workflow_call\n",
    "literal-scalar-strip": "on: |-\n  workflow_call\n",
    "literal-scalar-keep": "on: |+\n  workflow_call\n",
    "literal-scalar-indent": "on: |2\n  workflow_call\n",
    "sequence-folded-strip": "on:\n  - >-\n    workflow_call\n",
    "sequence-folded-keep": "on:\n  - >+\n    workflow_call\n",
    "sequence-folded-indent": "on:\n  - >2\n    workflow_call\n",
    "sequence-literal-strip": "on:\n  - |-\n    workflow_call\n",
    "sequence-literal-keep": "on:\n  - |+\n    workflow_call\n",
    "sequence-literal-indent": "on:\n  - |2\n    workflow_call\n",
    "scalar-tag": "on: !str workflow_call\n",
    "sequence-tag": "on:\n  - !str workflow_call\n",
    "mapping-key-tag": "on:\n  !str workflow_call:\n",
    "escaped-double-quoted-workflow-call": 'on: "workflow\\x5fcall"\n',
    "escaped-flow-quoted-workflow-call": 'on: [pull_request, "workflow\\u005fcall"]\n',
    "invalid-spaced-scalar": "on: pull request\n",
    "invalid-dotted-scalar": "on: pull.request\n",
    "invalid-leading-digit-scalar": "on: 123_event\n",
    "mapping-block-scalar-value": "on:\n  pull_request: >-\n    branches\n",
}


def _unsupported_actual_uses_cases(reusable: str) -> dict[str, str]:
    target_b = f"OpenCoven/.github/.github/workflows/{reusable}@{SHA_B}"
    return {
        "folded-scalar": f"    uses: >-\n      {target_b}\n",
        "folded-scalar-keep": f"    uses: >+\n      {target_b}\n",
        "folded-scalar-indent": f"    uses: >2\n      {target_b}\n",
        "literal-scalar": f"    uses: |-\n      {target_b}\n",
        "literal-scalar-keep": f"    uses: |+\n      {target_b}\n",
        "literal-scalar-indent": f"    uses: |2\n      {target_b}\n",
        "tagged-scalar": f"    uses: !str {target_b}\n",
        "commented-empty-value": f"    uses: # reviewed reusable target\n      {target_b}\n",
        "multiline-double-quoted": (
            f"    uses: \"OpenCoven/.github/.github/workflows/{reusable}@\n"
            f"      {SHA_B}\"\n"
        ),
        "escaped-double-quoted-prefix": (
            f"    uses: \"OpenCoven\\x2f.github/.github/workflows/{reusable}@{SHA_B}\"\n"
        ),
    }


UNSUPPORTED_DIRECT_CALLER_FORMS = {
    "quoted-uses-key": lambda reusable, path_input_name, path_input: _caller_workflow(
        reusable=reusable,
        path_input_name=path_input_name,
        path_input=path_input,
    ).replace("    uses: OpenCoven", '    "uses": OpenCoven'),
    "quoted-with-key": lambda reusable, path_input_name, path_input: _caller_workflow(
        reusable=reusable,
        path_input_name=path_input_name,
        path_input=path_input,
    ).replace("    with:\n", '    "with":\n'),
    "quoted-policy-ref-key": lambda reusable, path_input_name, path_input: _caller_workflow(
        reusable=reusable,
        path_input_name=path_input_name,
        path_input=path_input,
    ).replace("      policy_ref:", '      "policy_ref":'),
    "quoted-path-key": lambda reusable, path_input_name, path_input: _caller_workflow(
        reusable=reusable,
        path_input_name=path_input_name,
        path_input=path_input,
    ).replace(f"      {path_input_name}:", f'      "{path_input_name}":'),
    "quoted-jobs-key": lambda reusable, path_input_name, path_input: _caller_workflow(
        reusable=reusable,
        path_input_name=path_input_name,
        path_input=path_input,
    ).replace("jobs:\n", '"jobs":\n'),
    "flow-job-definition": lambda reusable, path_input_name, path_input: (
        "name: caller\n"
        "on: pull_request\n"
        "permissions:\n"
        "  contents: read\n"
        "jobs:\n"
        f"  readiness: {{ uses: OpenCoven/.github/.github/workflows/{reusable}@{SHA_A}, "
        f"with: {{ policy_ref: {SHA_A}, {path_input_name}: {path_input} }} }}\n"
    ),
    "malformed-job-indentation": lambda reusable, path_input_name, path_input: (
        "name: caller\n"
        "on: pull_request\n"
        "permissions:\n"
        "  contents: read\n"
        "jobs:\n"
        "    readiness:\n"
        f"    uses: OpenCoven/.github/.github/workflows/{reusable}@{SHA_A}\n"
        "    with:\n"
        f"      policy_ref: {SHA_A}\n"
        f"      {path_input_name}: {path_input}\n"
    ),
    "tagged-policy-ref": lambda reusable, path_input_name, path_input: _caller_workflow(
        reusable=reusable,
        path_input_name=path_input_name,
        path_input=path_input,
    ).replace(f"      policy_ref: {SHA_A}", f"      policy_ref: !str {SHA_A}"),
    "block-path-value": lambda reusable, path_input_name, path_input: _caller_workflow(
        reusable=reusable,
        path_input_name=path_input_name,
        path_input=path_input,
    ).replace(f"      {path_input_name}: {path_input}", f"      {path_input_name}: |-\n        {path_input}"),
}


class TrustedTargetPathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _write_json(self.root / "governance/repositories.json", _minimal_registry())
        _write_json(self.root / "agent/manifest.json", _minimal_manifest())
        _write_json(self.root / "evidence/packet.json", _minimal_evidence())
        (self.root / "agent/directory").mkdir()
        (self.root / "outside.txt").write_text("outside", encoding="utf-8")
        os.symlink(self.root / "agent/manifest.json", self.root / "agent/manifest-link.json")
        os.symlink(self.root / "outside.txt", self.root / "agent/outside-link.json")
        os.symlink(self.root.parent, self.root / "agent/root-escape")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_manifest_and_evidence_relative_paths_are_accepted(self) -> None:
        governance = GOV.Governance(self.root)
        self.assertEqual([], governance.validate_manifest_file(self.root, "agent/manifest.json", caller_repository="OpenCoven/coven-code"))
        self.assertEqual([], governance.validate_evidence_file(self.root, "evidence/packet.json"))

    def test_shell_metacharacters_are_literal_path_data(self) -> None:
        manifest_path = "agent/manifest;$(echo not-executed).json"
        evidence_path = "evidence/packet;$(echo not-executed).json"
        registry = _minimal_registry()
        registry["defaults"]["agent_manifest"]["path"] = manifest_path
        _write_json(self.root / "governance/repositories.json", registry)
        _write_json(self.root / manifest_path, _minimal_manifest())
        _write_json(self.root / evidence_path, _minimal_evidence())
        governance = GOV.Governance(self.root)
        self.assertEqual([], governance.validate_manifest_file(self.root, manifest_path, caller_repository="OpenCoven/coven-code"))
        self.assertEqual([], governance.validate_evidence_file(self.root, evidence_path))

    def test_invalid_manifest_paths_fail_closed(self) -> None:
        for value in (
            str(self.root / "agent/manifest.json"),
            "../agent/manifest.json",
            "agent/missing.json",
            "agent/directory",
            "agent/manifest\u0007.json",
            "agent/manifest-link.json",
            "agent/outside-link.json",
            "agent/root-escape/outside.txt",
        ):
            with self.subTest(path=value):
                errors = GOV.Governance(self.root).validate_manifest_file(self.root, value, caller_repository="OpenCoven/coven-code")
                self.assertTrue(errors, value)

    def test_evidence_must_be_json_below_evidence_directory(self) -> None:
        for value in ("agent/manifest.json", "evidence/../agent/manifest.json"):
            with self.subTest(path=value):
                errors = GOV.Governance(self.root).validate_evidence_file(self.root, value)
                self.assertTrue(errors, value)

    def test_evidence_requires_schema_required_fields(self) -> None:
        packet = _minimal_evidence()
        packet["change"].pop("non_goals")
        packet.pop("files")
        _write_json(self.root / "evidence/packet.json", packet)
        errors = GOV.Governance(self.root).validate_evidence_file(self.root, "evidence/packet.json")
        self.assertTrue(any("evidence.change.non_goals must be an array" in error for error in errors), errors)
        self.assertTrue(any("evidence.files must be an array" in error for error in errors), errors)

    def test_evidence_rejects_invalid_required_field_types(self) -> None:
        packet = _minimal_evidence()
        packet["files"] = "README.md"
        packet["authority"]["protected_boundaries"] = "boundary"
        _write_json(self.root / "evidence/packet.json", packet)
        errors = GOV.Governance(self.root).validate_evidence_file(self.root, "evidence/packet.json")
        self.assertTrue(any("evidence.files must be an array" in error for error in errors), errors)
        self.assertTrue(any("evidence.authority.protected_boundaries must be an array" in error for error in errors), errors)


class ReusableInvocationPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.workflow = self.root / ".github/workflows/caller.yml"
        self.workflow.parent.mkdir(parents=True)
        self.workflow.write_text(_caller_workflow(), encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _errors(self, *, policy_ref: str = SHA_A, runtime_path: str = "agent/manifest.json",
                workflow_ref_path: str = ".github/workflows/caller.yml",
                caller_repository: str = "OpenCoven/coven-code",
                reusable: str = "reusable-agent-readiness.yml",
                path_input_name: str = "manifest_path") -> list[str]:
        return GOV.validate_reusable_invocation(
            self.root,
            caller_workflow_ref=f"OpenCoven/coven-code/{workflow_ref_path}@refs/heads/main",
            caller_repository=caller_repository,
            policy_ref=policy_ref,
            reusable_workflow=reusable,
            path_input_name=path_input_name,
            runtime_path=runtime_path,
            default_runtime_path="agent/manifest.json" if path_input_name == "manifest_path" else None,
        )

    def _cli_result(self, *, reusable: str = "reusable-agent-readiness.yml",
                    path_input_name: str = "manifest_path",
                    runtime_path: str = "agent/manifest.json",
                    policy_ref: str = SHA_A) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            str(MODULE_PATH),
            "validate-reusable-invocation",
            "--target-root", str(self.root),
            "--caller-workflow-ref", "OpenCoven/coven-code/.github/workflows/caller.yml@refs/heads/main",
            "--caller-repository", "OpenCoven/coven-code",
            "--policy-ref", policy_ref,
            "--reusable-workflow", reusable,
            "--path-input-name", path_input_name,
            "--runtime-path", runtime_path,
        ]
        if path_input_name == "manifest_path":
            command.extend(["--default-runtime-path", "agent/manifest.json"])
        return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)

    def test_positive_direct_caller_with_exact_sha_is_accepted(self) -> None:
        self.assertEqual([], self._errors())

    def test_readiness_caller_cannot_disable_repository_check(self) -> None:
        self.workflow.write_text(
            _caller_workflow(extra_job="      run_repository_check: false\n"),
            encoding="utf-8",
        )
        errors = self._errors()
        self.assertTrue(any("run_repository_check" in error for error in errors), errors)

    def test_supported_literal_event_forms_are_accepted(self) -> None:
        cases = dict(SUPPORTED_EVENT_ON_BLOCKS)
        cases.update({
            "mapping-with-comment": "on:\n  pull_request: # reviewed event\n",
        })
        for name, on_block in cases.items():
            with self.subTest(case=name):
                self.workflow.write_text(_caller_workflow(on_block=on_block), encoding="utf-8")
                self.assertEqual([], self._errors())

    def test_round3_supported_event_forms_are_accepted_by_core_and_cli_for_both_reusables(self) -> None:
        reusable_cases = (
            ("reusable-agent-readiness.yml", "manifest_path", "agent/manifest.json"),
            ("reusable-evidence-packet.yml", "evidence_path", "evidence/packet.json"),
        )
        for reusable, path_input_name, runtime_path in reusable_cases:
            for name, on_block in SUPPORTED_EVENT_ON_BLOCKS.items():
                with self.subTest(reusable=reusable, case=name):
                    self.workflow.write_text(
                        _caller_workflow(
                            reusable=reusable,
                            path_input_name=path_input_name,
                            path_input=runtime_path,
                            on_block=on_block,
                        ),
                        encoding="utf-8",
                    )
                    self.assertEqual(
                        [],
                        self._errors(reusable=reusable, path_input_name=path_input_name, runtime_path=runtime_path),
                    )
                    result = self._cli_result(reusable=reusable, path_input_name=path_input_name, runtime_path=runtime_path)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_nested_workflow_call_event_variants_fail_closed(self) -> None:
        cases = {
            "quoted-mapping": 'on:\n  "workflow_call":\n',
            "flow-sequence": 'on: [pull_request, "workflow_call"]\n',
            "block-sequence": "on:\n  - pull_request\n  - workflow_call\n",
        }
        for name, on_block in cases.items():
            with self.subTest(case=name):
                self.workflow.write_text(_caller_workflow(on_block=on_block), encoding="utf-8")
                errors = self._errors()
                self.assertTrue(any("nested reusable workflow callers" in error for error in errors), errors)

    def test_unsupported_event_ambiguity_fails_closed(self) -> None:
        cases = dict(UNSUPPORTED_EVENT_ON_BLOCKS)
        cases.update({
            "flow-mapping": "on: { pull_request: null }\n",
            "duplicate-on": "on: pull_request\non: push\n",
            "duplicate-event": "on:\n  pull_request:\n  pull_request:\n",
        })
        for name, on_block in cases.items():
            with self.subTest(case=name):
                self.workflow.write_text(_caller_workflow(on_block=on_block), encoding="utf-8")
                self.assertTrue(self._errors())

    def test_round3_unsupported_event_forms_fail_core_and_cli_for_both_reusables(self) -> None:
        reusable_cases = (
            ("reusable-agent-readiness.yml", "manifest_path", "agent/manifest.json"),
            ("reusable-evidence-packet.yml", "evidence_path", "evidence/packet.json"),
        )
        for reusable, path_input_name, runtime_path in reusable_cases:
            for name, on_block in UNSUPPORTED_EVENT_ON_BLOCKS.items():
                with self.subTest(reusable=reusable, case=name):
                    self.workflow.write_text(
                        _caller_workflow(
                            reusable=reusable,
                            path_input_name=path_input_name,
                            path_input=runtime_path,
                            on_block=on_block,
                        ),
                        encoding="utf-8",
                    )
                    self.assertTrue(
                        self._errors(reusable=reusable, path_input_name=path_input_name, runtime_path=runtime_path)
                    )
                    result = self._cli_result(reusable=reusable, path_input_name=path_input_name, runtime_path=runtime_path)
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unsupported_actual_uses_forms_fail_before_decoy_matching_for_core_and_cli(self) -> None:
        reusable_cases = (
            ("reusable-agent-readiness.yml", "manifest_path", "agent/manifest.json"),
            ("reusable-evidence-packet.yml", "evidence_path", "evidence/packet.json"),
        )
        for reusable, path_input_name, runtime_path in reusable_cases:
            for name, actual_uses in _unsupported_actual_uses_cases(reusable).items():
                with self.subTest(reusable=reusable, case=name):
                    self.workflow.write_text(
                        _ambiguous_actual_uses_with_decoy(
                            reusable=reusable,
                            path_input_name=path_input_name,
                            path_input=runtime_path,
                            actual_uses=actual_uses,
                        ),
                        encoding="utf-8",
                    )
                    self.assertTrue(
                        self._errors(reusable=reusable, path_input_name=path_input_name, runtime_path=runtime_path)
                    )
                    result = self._cli_result(reusable=reusable, path_input_name=path_input_name, runtime_path=runtime_path)
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unsupported_direct_caller_key_forms_fail_core_and_cli_for_both_reusables(self) -> None:
        reusable_cases = (
            ("reusable-agent-readiness.yml", "manifest_path", "agent/manifest.json"),
            ("reusable-evidence-packet.yml", "evidence_path", "evidence/packet.json"),
        )
        for reusable, path_input_name, runtime_path in reusable_cases:
            for name, build in UNSUPPORTED_DIRECT_CALLER_FORMS.items():
                with self.subTest(reusable=reusable, case=name):
                    self.workflow.write_text(build(reusable, path_input_name, runtime_path), encoding="utf-8")
                    self.assertTrue(
                        self._errors(reusable=reusable, path_input_name=path_input_name, runtime_path=runtime_path)
                    )
                    result = self._cli_result(reusable=reusable, path_input_name=path_input_name, runtime_path=runtime_path)
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_exact_decoy_same_reusable_job_fails_closed(self) -> None:
        self.workflow.write_text(
            _decoy_caller_workflow(
                reusable="reusable-agent-readiness.yml",
                path_input_name="manifest_path",
                path_input="agent/manifest.json",
            ),
            encoding="utf-8",
        )
        errors = self._errors(policy_ref=SHA_B)
        self.assertTrue(errors)

    def test_inline_with_flow_mapping_fails_closed(self) -> None:
        self.workflow.write_text(
            _caller_workflow().replace(
                "    with:\n"
                f"      policy_ref: {SHA_A}\n"
                "      manifest_path: agent/manifest.json\n",
                f"    with: {{ policy_ref: {SHA_A}, manifest_path: agent/manifest.json }}\n",
            ),
            encoding="utf-8",
        )
        self.assertTrue(self._errors())

    def test_mismatching_uses_with_and_runtime_policy_shas_fail_closed(self) -> None:
        cases = {
            "uses": _caller_workflow(uses_ref=SHA_B),
            "with": _caller_workflow(policy_ref=SHA_B),
            "runtime": _caller_workflow(),
        }
        for name, text in cases.items():
            with self.subTest(case=name):
                self.workflow.write_text(text, encoding="utf-8")
                errors = self._errors(policy_ref=SHA_B if name == "runtime" else SHA_A)
                self.assertTrue(errors, errors)

    def test_branch_tag_and_malformed_refs_fail_closed(self) -> None:
        for ref in ("main", "v1", "refs/heads/main", "abc123"):
            with self.subTest(ref=ref):
                self.workflow.write_text(_caller_workflow(uses_ref=ref), encoding="utf-8")
                self.assertTrue(self._errors())

    def test_nested_caller_expressions_anchors_and_inherited_secrets_fail_closed(self) -> None:
        cases = (
            _caller_workflow(on_block="on:\n  workflow_call:\n"),
            _caller_workflow(policy_ref="${{ github.sha }}"),
            _caller_workflow(extra_job="    secrets: inherit\n"),
            _caller_workflow().replace("uses: OpenCoven", "uses: &reuse OpenCoven"),
        )
        for text in cases:
            with self.subTest(text=text):
                self.workflow.write_text(text, encoding="utf-8")
                self.assertTrue(self._errors())

    def test_wrong_workflow_name_and_caller_path_fail_closed(self) -> None:
        self.workflow.write_text(_caller_workflow(reusable="other.yml"), encoding="utf-8")
        self.assertTrue(self._errors())
        self.assertTrue(self._errors(workflow_ref_path=".github/actions/caller.yml"))

    def test_runtime_path_must_match_literal_caller_input_or_default(self) -> None:
        self.workflow.write_text(_caller_workflow(path_input=None), encoding="utf-8")
        self.assertEqual([], self._errors(runtime_path="agent/manifest.json"))
        self.assertTrue(self._errors(runtime_path="other.json"))
        self.workflow.write_text(_caller_workflow(path_input="${{ matrix.path }}"), encoding="utf-8")
        self.assertTrue(self._errors(runtime_path="agent/manifest.json"))

    def test_spoofed_caller_repository_fails_closed(self) -> None:
        self.assertTrue(self._errors(caller_repository="OpenCoven/coven"))


class InlineReusablePreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name)
        self.target = self.workspace / "target"
        self.workflow = self.target / ".github/workflows/caller.yml"
        self.workflow.parent.mkdir(parents=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _run_preflight(
        self,
        *,
        workflow_name: str,
        policy_ref: str,
        reusable: str,
        path_input_name: str,
        runtime_path: str,
        default_runtime_path: str = "",
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update({
            "POLICY_REF": policy_ref,
            "CALLER_REPOSITORY": "OpenCoven/coven-code",
            "CALLER_WORKFLOW_REF": "OpenCoven/coven-code/.github/workflows/caller.yml@refs/heads/main",
            "REUSABLE_WORKFLOW": reusable,
            "PATH_INPUT_NAME": path_input_name,
            "RUNTIME_PATH": runtime_path,
        })
        if default_runtime_path:
            env["DEFAULT_RUNTIME_PATH"] = default_runtime_path
        else:
            env.pop("DEFAULT_RUNTIME_PATH", None)
        return subprocess.run(
            [sys.executable, "-c", _extract_inline_preflight_script(workflow_name)],
            cwd=self.workspace,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_inline_preflight_rejects_exact_decoy_fixture_for_both_reusables(self) -> None:
        cases = (
            ("reusable-agent-readiness.yml", "manifest_path", "agent/manifest.json", "agent/manifest.json"),
            ("reusable-evidence-packet.yml", "evidence_path", "evidence/packet.json", ""),
        )
        for workflow_name, path_input_name, runtime_path, default_path in cases:
            with self.subTest(workflow=workflow_name):
                self.workflow.write_text(
                    _decoy_caller_workflow(
                        reusable=workflow_name,
                        path_input_name=path_input_name,
                        path_input=runtime_path,
                    ),
                    encoding="utf-8",
                )
                result = self._run_preflight(
                    workflow_name=workflow_name,
                    policy_ref=SHA_B,
                    reusable=workflow_name,
                    path_input_name=path_input_name,
                    runtime_path=runtime_path,
                    default_runtime_path=default_path,
                )
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inline_preflight_accepts_supported_callers_for_both_reusables(self) -> None:
        cases = (
            (
                "reusable-agent-readiness.yml",
                _caller_workflow(path_input=None),
                "manifest_path",
                "agent/manifest.json",
                "agent/manifest.json",
            ),
            (
                "reusable-evidence-packet.yml",
                _caller_workflow(
                    reusable="reusable-evidence-packet.yml",
                    path_input="evidence/packet.json",
                    path_input_name="evidence_path",
                ),
                "evidence_path",
                "evidence/packet.json",
                "",
            ),
        )
        for workflow_name, text, path_input_name, runtime_path, default_path in cases:
            with self.subTest(workflow=workflow_name):
                self.workflow.write_text(text, encoding="utf-8")
                result = self._run_preflight(
                    workflow_name=workflow_name,
                    policy_ref=SHA_A,
                    reusable=workflow_name,
                    path_input_name=path_input_name,
                    runtime_path=runtime_path,
                    default_runtime_path=default_path,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inline_readiness_preflight_rejects_disabled_repository_check(self) -> None:
        self.workflow.write_text(
            _caller_workflow(extra_job="      run_repository_check: false\n"),
            encoding="utf-8",
        )
        result = self._run_preflight(
            workflow_name="reusable-agent-readiness.yml",
            policy_ref=SHA_A,
            reusable="reusable-agent-readiness.yml",
            path_input_name="manifest_path",
            runtime_path="agent/manifest.json",
            default_runtime_path="agent/manifest.json",
        )
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("run_repository_check", result.stderr)

    def test_readiness_workflow_always_runs_repository_check(self) -> None:
        text = (ROOT / ".github/workflows/reusable-agent-readiness.yml").read_text(encoding="utf-8")
        self.assertNotIn("run_repository_check:", text)
        self.assertNotIn("if: ${{ inputs.run_repository_check }}", text)

    def test_inline_preflight_rejects_nested_event_variants_for_both_reusables(self) -> None:
        nested_events = (
            'on:\n  "workflow_call":\n',
            'on: [pull_request, "workflow_call"]\n',
            "on:\n  - pull_request\n  - workflow_call\n",
        )
        for workflow_name, path_input_name, runtime_path, default_path in (
            ("reusable-agent-readiness.yml", "manifest_path", "agent/manifest.json", "agent/manifest.json"),
            ("reusable-evidence-packet.yml", "evidence_path", "evidence/packet.json", ""),
        ):
            for on_block in nested_events:
                with self.subTest(workflow=workflow_name, on_block=on_block):
                    self.workflow.write_text(
                        _caller_workflow(
                            reusable=workflow_name,
                            path_input=runtime_path,
                            path_input_name=path_input_name,
                            on_block=on_block,
                        ),
                        encoding="utf-8",
                    )
                    result = self._run_preflight(
                        workflow_name=workflow_name,
                        policy_ref=SHA_A,
                        reusable=workflow_name,
                        path_input_name=path_input_name,
                        runtime_path=runtime_path,
                        default_runtime_path=default_path,
                    )
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn("nested reusable workflow callers", result.stderr)

    def test_round3_inline_preflight_event_table_for_both_reusables(self) -> None:
        reusable_cases = (
            ("reusable-agent-readiness.yml", "manifest_path", "agent/manifest.json", "agent/manifest.json"),
            ("reusable-evidence-packet.yml", "evidence_path", "evidence/packet.json", ""),
        )
        for workflow_name, path_input_name, runtime_path, default_path in reusable_cases:
            for name, on_block in SUPPORTED_EVENT_ON_BLOCKS.items():
                with self.subTest(workflow=workflow_name, case=name, expected="accepted"):
                    self.workflow.write_text(
                        _caller_workflow(
                            reusable=workflow_name,
                            path_input=runtime_path,
                            path_input_name=path_input_name,
                            on_block=on_block,
                        ),
                        encoding="utf-8",
                    )
                    result = self._run_preflight(
                        workflow_name=workflow_name,
                        policy_ref=SHA_A,
                        reusable=workflow_name,
                        path_input_name=path_input_name,
                        runtime_path=runtime_path,
                        default_runtime_path=default_path,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for name, on_block in UNSUPPORTED_EVENT_ON_BLOCKS.items():
                with self.subTest(workflow=workflow_name, case=name, expected="rejected"):
                    self.workflow.write_text(
                        _caller_workflow(
                            reusable=workflow_name,
                            path_input=runtime_path,
                            path_input_name=path_input_name,
                            on_block=on_block,
                        ),
                        encoding="utf-8",
                    )
                    result = self._run_preflight(
                        workflow_name=workflow_name,
                        policy_ref=SHA_A,
                        reusable=workflow_name,
                        path_input_name=path_input_name,
                        runtime_path=runtime_path,
                        default_runtime_path=default_path,
                    )
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inline_preflight_rejects_unsupported_actual_uses_before_decoy_matching(self) -> None:
        reusable_cases = (
            ("reusable-agent-readiness.yml", "manifest_path", "agent/manifest.json", "agent/manifest.json"),
            ("reusable-evidence-packet.yml", "evidence_path", "evidence/packet.json", ""),
        )
        for workflow_name, path_input_name, runtime_path, default_path in reusable_cases:
            for name, actual_uses in _unsupported_actual_uses_cases(workflow_name).items():
                with self.subTest(workflow=workflow_name, case=name):
                    self.workflow.write_text(
                        _ambiguous_actual_uses_with_decoy(
                            reusable=workflow_name,
                            path_input_name=path_input_name,
                            path_input=runtime_path,
                            actual_uses=actual_uses,
                        ),
                        encoding="utf-8",
                    )
                    result = self._run_preflight(
                        workflow_name=workflow_name,
                        policy_ref=SHA_A,
                        reusable=workflow_name,
                        path_input_name=path_input_name,
                        runtime_path=runtime_path,
                        default_runtime_path=default_path,
                    )
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inline_preflight_rejects_unsupported_direct_caller_key_forms(self) -> None:
        reusable_cases = (
            ("reusable-agent-readiness.yml", "manifest_path", "agent/manifest.json", "agent/manifest.json"),
            ("reusable-evidence-packet.yml", "evidence_path", "evidence/packet.json", ""),
        )
        for workflow_name, path_input_name, runtime_path, default_path in reusable_cases:
            for name, build in UNSUPPORTED_DIRECT_CALLER_FORMS.items():
                with self.subTest(workflow=workflow_name, case=name):
                    self.workflow.write_text(build(workflow_name, path_input_name, runtime_path), encoding="utf-8")
                    result = self._run_preflight(
                        workflow_name=workflow_name,
                        policy_ref=SHA_A,
                        reusable=workflow_name,
                        path_input_name=path_input_name,
                        runtime_path=runtime_path,
                        default_runtime_path=default_path,
                    )
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


class ManifestRegistryBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _write_json(self.root / "governance/repositories.json", _minimal_registry())
        _write_json(self.root / "agent/manifest.json", _minimal_manifest())

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _manifest_errors(self, manifest: dict | None = None, *, caller_repository: str = "OpenCoven/coven-code") -> list[str]:
        if manifest is not None:
            _write_json(self.root / "agent/manifest.json", manifest)
        return GOV.Governance(self.root).validate_manifest_file(
            self.root,
            "agent/manifest.json",
            caller_repository=caller_repository,
        )

    def test_manifest_repository_is_bound_to_actual_caller(self) -> None:
        manifest = _minimal_manifest(repo="coven")
        self.assertTrue(self._manifest_errors(manifest), "self-declared repository name must not select registry entry")

    def test_unregistered_caller_and_registry_field_mismatch_fail_closed(self) -> None:
        self.assertTrue(self._manifest_errors(caller_repository="OpenCoven/not-registered"))
        manifest = _minimal_manifest()
        manifest["repository"]["owner"] = "SomeoneElse"
        manifest["repository"]["does_not_own"] = []
        self.assertTrue(self._manifest_errors(manifest))

    def test_r3_r4_manifests_require_protected_paths_and_canonical_adapters(self) -> None:
        manifest = _minimal_manifest()
        manifest["risk"]["protected_paths"] = []
        self.assertTrue(self._manifest_errors(manifest))
        manifest = _minimal_manifest()
        manifest["agent"]["bootstrap"] = "python bootstrap.py"
        manifest["agent"]["verify"]["fast"] = "pytest"
        manifest["agent"]["verify"]["full"] = "pytest -q"
        self.assertTrue(self._manifest_errors(manifest))


class GeneratedOutputTests(unittest.TestCase):
    def test_generation_is_deterministic(self) -> None:
        governance = GOV.Governance(ROOT)
        first = governance.generated_content()
        second = governance.generated_content()
        self.assertEqual(first, second)

    def test_portfolio_exposes_unresolved_observation_status(self) -> None:
        portfolio = GOV.Governance(ROOT).generated_content()["generated/portfolio.md"]
        self.assertIn("| Observation |", portfolio)
        self.assertRegex(
            portfolio,
            r"(?m)^\| opencoven-beta-august-hackathon-2026 .*"
            r"\| unavailable-needs-owner-evidence \|$",
        )


class PublishedSchemaTests(unittest.TestCase):
    def _copy_repository(self, target: Path) -> None:
        shutil.copytree(
            ROOT,
            target,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )

    def test_contract_index_missing_schema_fields_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._copy_repository(root)
            path = root / "compatibility/contracts.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data.pop("schema_version")
            data.pop("claim_rule")
            data["contracts"][0].pop("status")
            data["contracts"][0].pop("immutable_release_required")
            _write_json(path, data)

            errors = GOV.Governance(root).validate()

            for field in ("schema_version", "claim_rule", "status", "immutable_release_required"):
                self.assertTrue(any("schema" in error and field in error for error in errors), (field, errors))

    def test_repository_internal_json_is_outside_governance_schema_scope(self) -> None:
        errors = GOV.Governance(ROOT).validate()
        self.assertFalse(any(".git/" in error and "schema reference" in error for error in errors), errors)

    def test_initiative_schema_enums_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._copy_repository(root)
            path = root / "initiatives/organization-governance-plane-v1.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["status"] = "almost-done"
            data["priority"] = "urgent"
            data["ownership_status"] = "someone-probably-owns-it"
            _write_json(path, data)

            errors = GOV.Governance(root).validate()

            for field in ("status", "priority", "ownership_status"):
                self.assertTrue(any("schema" in error and field in error for error in errors), (field, errors))


class GovernancePolicyConsistencyTests(unittest.TestCase):
    def test_public_documents_do_not_name_private_design_inventory(self) -> None:
        private_name = "coven-" + "design"
        prohibited = (
            f"private `OpenCoven/{private_name}`",
            f"[`OpenCoven/{private_name}`](https://github.com/OpenCoven/{private_name})",
            f"private {private_name}",
        )
        matches: list[str] = []
        for path in sorted((ROOT / "docs").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for value in prohibited:
                if value in text:
                    matches.append(f"{path.relative_to(ROOT)}: {value}")
        self.assertEqual([], matches)

    def test_rollout_protects_main_before_ratifying_merge(self) -> None:
        text = (ROOT / "docs/rollout.md").read_text(encoding="utf-8")
        phrases = (
            "Establish an eligible independent reviewer",
            "Apply and evidence the `.github/main` ruleset",
            "Review and merge the governance-plane PR",
        )
        for phrase in phrases:
            self.assertIn(phrase, text)
        reviewer, protection, merge = (text.index(phrase) for phrase in phrases)
        self.assertLess(reviewer, protection)
        self.assertLess(protection, merge)

    def test_evidence_packet_does_not_claim_pre_pr_state(self) -> None:
        text = (ROOT / "evidence/2026-09-03-organization-governance-plane-v1.json").read_text(encoding="utf-8")
        self.assertNotIn("13 unit tests", text)
        self.assertNotIn("Pending creation of the review branch and pull request", text)
        self.assertIn("97 tests", text)
        self.assertIn("535177155710425b8f9e5ad546245c77ace35c20", text)


class PublicDriftTests(unittest.TestCase):
    def setUp(self) -> None:
        self.governance = GOV.Governance(ROOT)
        self.registry = GOV.expanded_repositories(self.governance.registry())
        self.live = [
            {
                "name": item["name"],
                "visibility": "public",
                "private": False,
                "archived": item["observed"]["archived"],
                "default_branch": item["observed"]["default_branch"],
            }
            for item in self.registry
        ]

    def test_matching_public_inventory_has_no_drift(self) -> None:
        declared = self.governance.registry_map()
        declared["opencoven-beta-august-hackathon-2026"]["observation_status"] = "verified-public"
        with patch.object(self.governance, "registry_map", return_value=declared):
            self.assertEqual([], GOV.reconcile_public_inventory(self.governance, self.live))

    def test_visible_repository_marked_unavailable_is_reported(self) -> None:
        errors = GOV.reconcile_public_inventory(self.governance, self.live)
        self.assertTrue(
            any(
                "`opencoven-beta-august-hackathon-2026` observation status mismatch" in error
                and "live=verified-public" in error
                for error in errors
            ),
            errors,
        )

    def test_unregistered_public_repository_is_reported(self) -> None:
        live = self.live + [{
            "name": "unexpected-public-repository",
            "visibility": "public",
            "private": False,
            "archived": False,
            "default_branch": "main",
        }]
        errors = GOV.reconcile_public_inventory(self.governance, live)
        self.assertTrue(any("unregistered public repository" in error for error in errors), errors)


class GitHubRequestTests(unittest.TestCase):
    def test_authenticated_request_uses_bearer_token(self) -> None:
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self) -> bytes:
                return b"{}"

        with patch.object(governance_cli.urllib.request, "urlopen", return_value=Response()) as urlopen:
            governance_cli.github_request("https://api.github.com/user", token="test-token")

        request = urlopen.call_args.args[0]
        self.assertEqual("Bearer test-token", request.get_header("Authorization"))


def _raw_node(number: int, *, title: str = GOV.MANAGED_ISSUE_TITLE, marker: str | None = GOV.MANAGED_ISSUE_MARKER,
              login: str = governance_cli.GRAPHQL_BOT_LOGIN, typename: str | None = governance_cli.GRAPHQL_BOT_TYPENAME,
              node_id: str | None = None) -> dict:
    """Build a raw GraphQL `Issue` node as returned inside a `nodes` array.

    Defaults to the real GraphQL Actions-bot author shape: `__typename: "Bot"`
    with the unsuffixed `login: "github-actions"` (GraphQL never reports the
    REST-style `github-actions[bot]` login)."""
    return {
        "id": node_id or f"ISSUE_NODE_{number}",
        "number": number,
        "title": title,
        "body": f"{marker}\nsome drift body" if marker else "no marker here",
        "author": {"__typename": typename, "login": login},
    }


def _raw_filler(number: int) -> dict:
    return _raw_node(number, title=f"unrelated issue {number}", marker=None, login="some-human", typename="User")


def _gql_page(nodes: list[dict], *, has_next: bool, end_cursor: str | None) -> dict:
    return {
        "data": {
            "repository": {
                "issues": {
                    "pageInfo": {"hasNextPage": has_next, "endCursor": end_cursor},
                    "nodes": nodes,
                }
            }
        }
    }


def _flat_issue(number: int, *, title: str = GOV.MANAGED_ISSUE_TITLE, marker: str = GOV.MANAGED_ISSUE_MARKER,
                login: str = GOV.MANAGED_ISSUE_AUTHOR) -> dict:
    """Build an already-validated flattened issue dict, the shape
    `find_managed_drift_issue` consumes after `_validate_issue_node`."""
    return {"id": f"ISSUE_NODE_{number}", "number": number, "title": title, "body": f"{marker}\nsome drift body", "login": login}


def _flat_filler(number: int) -> dict:
    return {"id": f"ISSUE_NODE_{number}", "number": number, "title": f"unrelated issue {number}", "body": "no marker here", "login": "some-human"}


def _rest_issue(number: int, *, title: str = GOV.MANAGED_ISSUE_TITLE, marker: str | None = GOV.MANAGED_ISSUE_MARKER,
                 login: str = GOV.MANAGED_ISSUE_AUTHOR, is_pull_request: bool = False) -> dict:
    """Build a raw REST `/issues` list item (the shape fetch_open_issues_readonly consumes)."""
    issue = {
        "number": number,
        "title": title,
        "body": f"{marker}\nsome drift body" if marker else "no marker here",
        "user": {"login": login},
    }
    if is_pull_request:
        issue["pull_request"] = {"url": f"https://api.github.com/repos/OpenCoven/.github/pulls/{number}"}
    return issue


def _rest_filler(number: int) -> dict:
    return _rest_issue(number, title=f"unrelated issue {number}", marker=None, login="some-human")


def _rest_get_calls(mocked) -> list:
    return [c for c in mocked.call_args_list if c.args[0] != governance_cli.GRAPHQL_ENDPOINT]


def _graphql_calls(mocked) -> list:
    return [c for c in mocked.call_args_list if c.args[0] == governance_cli.GRAPHQL_ENDPOINT]


def _rest_post_calls(mocked) -> list:
    return [c for c in mocked.call_args_list if c.kwargs.get("method") == "POST" and c.args[0] != governance_cli.GRAPHQL_ENDPOINT]


def _patch_calls(mocked) -> list:
    return [c for c in mocked.call_args_list if c.kwargs.get("method") == "PATCH"]


class DriftIssueScanTests(unittest.TestCase):
    """Regression coverage for the GraphQL cursor-based open-issue scan used by
    upsert_drift_issue, and for the closed managed-issue-creation race.

    REST page-number pagination is unsafe over a mutable open-issue
    collection: closing an earlier issue between two `page=N` requests
    shifts every later issue left by one slot, which can make a managed
    issue about to cross a page boundary vanish from the scan entirely, or
    cause a boundary issue to be returned on two consecutive pages. These
    tests exercise the GraphQL cursor-based replacement, which identifies
    pagination position relative to an already-returned node rather than an
    absolute offset, and prove that any inconsistency it cannot resolve
    (duplicate node ids, a stalled cursor, or malformed shapes) fails closed
    instead of silently returning a partial, skipped, or duplicated result.
    """

    def test_managed_issue_on_second_page_is_updated_not_duplicated(self) -> None:
        # 101 total open issues: a full 100-item first GraphQL page of
        # unrelated issues, plus the real managed issue only on the second
        # page (reached via the page-one endCursor).
        page_one_nodes = [_raw_filler(i) for i in range(1, 101)]
        page_two_nodes = [_raw_node(101)]

        def fake_github_request(url, *, token=None, method="GET", payload=None):
            if url == governance_cli.GRAPHQL_ENDPOINT:
                after = payload["variables"]["after"]
                if after is None:
                    return _gql_page(page_one_nodes, has_next=True, end_cursor="cursor-1")
                if after == "cursor-1":
                    return _gql_page(page_two_nodes, has_next=False, end_cursor=None)
                self.fail(f"unexpected cursor: {after}")
            self.assertEqual(method, "PATCH", f"unexpected REST request: {method} {url}")
            return {"number": 101}

        with patch.object(governance_cli, "github_request", side_effect=fake_github_request) as mocked:
            GOV.upsert_drift_issue("OpenCoven/.github", "token", ["some drift"], dry_run=False)

        self.assertEqual(len(_rest_post_calls(mocked)), 0, "must not create a duplicate managed issue")
        patch_calls = _patch_calls(mocked)
        self.assertEqual(len(patch_calls), 1, "must update the existing managed issue")
        self.assertEqual(patch_calls[0].args[0], "https://api.github.com/repos/OpenCoven/.github/issues/101")

    def test_fetch_open_issues_paginates_beyond_first_page(self) -> None:
        page_one_nodes = [_raw_filler(i) for i in range(1, 101)]
        page_two_nodes = [_raw_filler(101)]

        def fake_github_request(url, *, token=None, method="GET", payload=None):
            after = payload["variables"]["after"]
            if after is None:
                return _gql_page(page_one_nodes, has_next=True, end_cursor="cursor-1")
            if after == "cursor-1":
                return _gql_page(page_two_nodes, has_next=False, end_cursor=None)
            self.fail(f"unexpected cursor: {after}")

        with patch.object(governance_cli, "github_request", side_effect=fake_github_request):
            issues = governance_cli.fetch_open_issues("OpenCoven", ".github", "token")
        self.assertEqual(len(issues), 101)

    def test_boundary_duplicate_node_id_across_pages_fails_closed(self) -> None:
        # Simulates a mutation-induced boundary duplicate: the same
        # underlying issue is returned by both the first and second page
        # (for example because an insertion/deletion shifted the connection
        # between requests). A scan must never silently accept this: it
        # would either double-count an unrelated issue or, worse, mask a
        # real skip elsewhere in the traversal.
        duplicate = _raw_node(101, node_id="ISSUE_NODE_101")

        def fake_github_request(url, *, token=None, method="GET", payload=None):
            after = payload["variables"]["after"]
            if after is None:
                return _gql_page([duplicate], has_next=True, end_cursor="cursor-1")
            if after == "cursor-1":
                return _gql_page([duplicate], has_next=False, end_cursor=None)
            self.fail(f"unexpected cursor: {after}")

        with patch.object(governance_cli, "github_request", side_effect=fake_github_request):
            with self.assertRaises(RuntimeError):
                governance_cli.fetch_open_issues("OpenCoven", ".github", "token")

    def test_repeated_cursor_without_progress_fails_closed(self) -> None:
        # Simulates a collection mutation that leaves the connection unable
        # to make forward progress (the same endCursor reported twice). A
        # scan must fail closed rather than loop forever or silently return
        # a truncated result.
        def fake_github_request(url, *, token=None, method="GET", payload=None):
            after = payload["variables"]["after"]
            if after is None:
                return _gql_page([_raw_filler(1)], has_next=True, end_cursor="cursor-1")
            if after == "cursor-1":
                return _gql_page([], has_next=True, end_cursor="cursor-1")
            self.fail(f"unexpected cursor: {after}")

        with patch.object(governance_cli, "github_request", side_effect=fake_github_request):
            with self.assertRaises(RuntimeError):
                governance_cli.fetch_open_issues("OpenCoven", ".github", "token")

    def test_missing_end_cursor_with_has_next_page_fails_closed(self) -> None:
        with patch.object(
            governance_cli, "github_request",
            return_value=_gql_page([_raw_filler(1)], has_next=True, end_cursor=None),
        ):
            with self.assertRaises(RuntimeError):
                governance_cli.fetch_open_issues("OpenCoven", ".github", "token")

    def test_malformed_page_info_is_rejected(self) -> None:
        malformed = {"data": {"repository": {"issues": {"pageInfo": {"hasNextPage": "yes"}, "nodes": []}}}}
        with patch.object(governance_cli, "github_request", return_value=malformed):
            with self.assertRaises(RuntimeError):
                governance_cli.fetch_open_issues("OpenCoven", ".github", "token")

    def test_malformed_issue_node_is_rejected(self) -> None:
        malformed_node = {"id": "ISSUE_NODE_1", "title": "missing number field"}
        with patch.object(
            governance_cli, "github_request",
            return_value=_gql_page([malformed_node], has_next=False, end_cursor=None),
        ):
            with self.assertRaises(RuntimeError):
                governance_cli.fetch_open_issues("OpenCoven", ".github", "token")

    def test_malformed_top_level_response_is_rejected(self) -> None:
        with patch.object(governance_cli, "github_request", return_value={"message": "not found"}):
            with self.assertRaises(RuntimeError):
                governance_cli.fetch_open_issues("OpenCoven", ".github", "token")

    def test_ambiguous_managed_issues_fail_closed(self) -> None:
        issues = [_flat_issue(1), _flat_issue(2)]
        with self.assertRaises(RuntimeError):
            GOV.find_managed_drift_issue(issues, marker=GOV.MANAGED_ISSUE_MARKER, title=GOV.MANAGED_ISSUE_TITLE)

    def test_spoofed_issue_from_untrusted_author_fails_closed(self) -> None:
        issues = [_flat_issue(1, login="an-attacker")]
        with self.assertRaises(RuntimeError):
            GOV.find_managed_drift_issue(issues, marker=GOV.MANAGED_ISSUE_MARKER, title=GOV.MANAGED_ISSUE_TITLE)

    def test_real_graphql_bot_identity_is_recognized_end_to_end(self) -> None:
        # GitHub's two APIs report the scheduled Actions bot's identity
        # differently: REST reports `user.login == "github-actions[bot]"`,
        # while GraphQL's `author` union reports the unsuffixed
        # `login == "github-actions"` together with `__typename == "Bot"`.
        # Before normalization, comparing the raw GraphQL login directly
        # against the REST-shaped `MANAGED_ISSUE_AUTHOR` constant rejected
        # the workflow's own previously-created issue as spoofed. This
        # exercises the full path (raw GraphQL node -> `_validate_issue_node`
        # normalization -> `find_managed_drift_issue`) with the exact real
        # API shape and proves the managed issue is now recognized and
        # trusted rather than treated as ambiguous/suspicious.
        raw_node = _raw_node(101)  # defaults to __typename="Bot", login="github-actions"
        flattened = governance_cli._validate_issue_node(raw_node, owner="OpenCoven", repo=".github", index=0)
        self.assertEqual(flattened["login"], GOV.MANAGED_ISSUE_AUTHOR)
        found = GOV.find_managed_drift_issue([flattened], marker=GOV.MANAGED_ISSUE_MARKER, title=GOV.MANAGED_ISSUE_TITLE)
        self.assertIsNotNone(found, "the real GraphQL bot identity must be recognized as the managed issue")
        self.assertEqual(found["number"], 101)

    def test_non_bot_typename_with_matching_login_is_not_implicitly_trusted(self) -> None:
        # A `User` (or any non-`Bot` typename) whose login happens to equal
        # the bot's unsuffixed GraphQL login ("github-actions") must never
        # be normalized to the canonical managed identity: normalization is
        # keyed on the exact (__typename, login) pair, not login alone.
        spoofing_node = _raw_node(202, login=governance_cli.GRAPHQL_BOT_LOGIN, typename="User")
        flattened = governance_cli._validate_issue_node(spoofing_node, owner="OpenCoven", repo=".github", index=0)
        self.assertEqual(flattened["login"], governance_cli.GRAPHQL_BOT_LOGIN, "must not be rewritten to the canonical bot login")
        self.assertNotEqual(flattened["login"], GOV.MANAGED_ISSUE_AUTHOR)
        with self.assertRaises(RuntimeError):
            GOV.find_managed_drift_issue([flattened], marker=GOV.MANAGED_ISSUE_MARKER, title=GOV.MANAGED_ISSUE_TITLE)

    def test_no_matching_issue_returns_none(self) -> None:
        issues = [_flat_filler(1), _flat_filler(2)]
        self.assertIsNone(
            GOV.find_managed_drift_issue(issues, marker=GOV.MANAGED_ISSUE_MARKER, title=GOV.MANAGED_ISSUE_TITLE)
        )

    def test_pre_create_revalidation_prevents_duplicate_when_managed_issue_appears_between_scans(self) -> None:
        # The initial scan finds nothing (only unrelated issues). Before the
        # fix, upsert_drift_issue would immediately POST a new managed
        # issue. Simulate a concurrent reconciler run creating the managed
        # issue in the window between the initial scan and this POST: the
        # pre-create revalidation scan must find it and PATCH instead of
        # creating a duplicate.
        scans_completed = {"count": 0}

        def fake_github_request(url, *, token=None, method="GET", payload=None):
            if url == governance_cli.GRAPHQL_ENDPOINT:
                self.assertIsNone(payload["variables"]["after"], "test only uses single-page scans")
                scans_completed["count"] += 1
                if scans_completed["count"] == 1:
                    return _gql_page([_raw_filler(1)], has_next=False, end_cursor=None)
                return _gql_page([_raw_node(202)], has_next=False, end_cursor=None)
            self.assertEqual(method, "PATCH", f"unexpected REST request: {method} {url}")
            return {"number": 202}

        with patch.object(governance_cli, "github_request", side_effect=fake_github_request) as mocked:
            GOV.upsert_drift_issue("OpenCoven/.github", "token", ["some drift"], dry_run=False)

        self.assertEqual(scans_completed["count"], 2, "must scan twice: initial scan, then pre-create revalidation")
        self.assertEqual(len(_rest_post_calls(mocked)), 0, "revalidation must prevent the duplicate POST")
        patch_calls = _patch_calls(mocked)
        self.assertEqual(len(patch_calls), 1, "revalidation must PATCH the concurrently created managed issue")
        self.assertEqual(patch_calls[0].args[0], "https://api.github.com/repos/OpenCoven/.github/issues/202")

    def test_pre_create_revalidation_ambiguity_fails_closed_instead_of_creating(self) -> None:
        # If the revalidation scan itself becomes ambiguous (for example two
        # concurrent runs both created a managed-looking issue), the
        # observer must refuse to act rather than guessing or creating a
        # third duplicate.
        scans_completed = {"count": 0}

        def fake_github_request(url, *, token=None, method="GET", payload=None):
            if url == governance_cli.GRAPHQL_ENDPOINT:
                scans_completed["count"] += 1
                if scans_completed["count"] == 1:
                    return _gql_page([], has_next=False, end_cursor=None)
                return _gql_page(
                    [_raw_node(202, node_id="ISSUE_NODE_202"), _raw_node(203, node_id="ISSUE_NODE_203")],
                    has_next=False, end_cursor=None,
                )
            self.fail(f"unexpected non-GraphQL request: {method} {url}")

        with patch.object(governance_cli, "github_request", side_effect=fake_github_request) as mocked:
            with self.assertRaises(RuntimeError):
                GOV.upsert_drift_issue("OpenCoven/.github", "token", ["some drift"], dry_run=False)

        self.assertEqual(len(_rest_post_calls(mocked)), 0, "must never create on an ambiguous revalidation")

    def test_authenticated_mutating_run_uses_graphql_scan(self) -> None:
        # A non-dry-run call with a token must use the consistent GraphQL
        # cursor scan (never the REST offset scan), since it is the only
        # path allowed to PATCH/POST.
        def fake_github_request(url, *, token=None, method="GET", payload=None):
            if url == governance_cli.GRAPHQL_ENDPOINT:
                return _gql_page([_raw_node(101)], has_next=False, end_cursor=None)
            self.assertEqual(method, "PATCH", f"unexpected REST request: {method} {url}")
            return {"number": 101}

        with patch.object(governance_cli, "github_request", side_effect=fake_github_request) as mocked:
            GOV.upsert_drift_issue("OpenCoven/.github", "token", ["some drift"], dry_run=False)

        self.assertEqual(len(_graphql_calls(mocked)), 1)
        self.assertEqual(len(_rest_get_calls(mocked)), 1, "the single REST call must be the PATCH, not a GET scan")


class TokenlessDryRunTests(unittest.TestCase):
    """Regression coverage for the documented unauthenticated `--dry-run` contract.

    `command_reconcile` explicitly allows `--dry-run` without `GITHUB_TOKEN`,
    but `upsert_drift_issue` previously always scanned via GraphQL, which
    requires a token — an unauthenticated GraphQL POST is rejected/rate
    limited, breaking the documented tokenless dry-run path outright. These
    tests prove: (1) a tokenless dry-run never calls the GraphQL endpoint
    and instead uses the read-only REST scan, while still reporting drift or
    close intent as applicable; (2) a non-dry-run call without a token
    remains rejected, both at the `command_reconcile` gate and, in depth,
    inside `upsert_drift_issue` itself; and (3) authenticated runs are
    unaffected and still use the GraphQL scan plus pre-create revalidation
    (covered by `DriftIssueScanTests`).
    """

    def test_tokenless_dry_run_with_drift_reports_body_via_rest_scan_only(self) -> None:
        page_one = [_rest_filler(i) for i in range(1, 101)]
        page_two = [_rest_filler(101)]  # no managed issue exists yet

        def fake_github_request(url, *, token=None, method="GET", payload=None):
            self.assertIsNone(token, "tokenless dry-run must never attach a token")
            if "page=2" in url:
                return page_two
            if "page=1" in url:
                return page_one
            self.fail(f"unexpected request: {method} {url}")

        with patch.object(governance_cli, "github_request", side_effect=fake_github_request) as mocked:
            with redirect_stdout(io.StringIO()) as out:
                GOV.upsert_drift_issue("OpenCoven/.github", "", ["some drift"], dry_run=True)

        self.assertEqual(len(_graphql_calls(mocked)), 0, "tokenless dry-run must never call GraphQL")
        self.assertEqual(len(mocked.call_args_list), 2, "must use the REST scan, paginated")
        self.assertIn(GOV.MANAGED_ISSUE_MARKER, out.getvalue())
        self.assertIn("some drift", out.getvalue())

    def test_tokenless_dry_run_with_existing_managed_issue_and_no_drift_reports_close_intent(self) -> None:
        issues = [_rest_filler(1), _rest_issue(2), _rest_filler(3)]

        def fake_github_request(url, *, token=None, method="GET", payload=None):
            self.assertIsNone(token, "tokenless dry-run must never attach a token")
            if "page=1" in url:
                return issues
            self.fail(f"unexpected request: {method} {url}")

        with patch.object(governance_cli, "github_request", side_effect=fake_github_request) as mocked:
            with redirect_stdout(io.StringIO()) as out:
                GOV.upsert_drift_issue("OpenCoven/.github", "", [], dry_run=True)

        self.assertEqual(len(_graphql_calls(mocked)), 0, "tokenless dry-run must never call GraphQL")
        self.assertIn("would close clean drift issue #2", out.getvalue())

    def test_tokenless_dry_run_ignores_pull_requests_and_untrusted_marker_holders(self) -> None:
        issues = [_rest_filler(1), _rest_issue(2, is_pull_request=True)]

        def fake_github_request(url, *, token=None, method="GET", payload=None):
            return issues if "page=1" in url else self.fail(f"unexpected request: {url}")

        with patch.object(governance_cli, "github_request", side_effect=fake_github_request):
            with redirect_stdout(io.StringIO()) as out:
                GOV.upsert_drift_issue("OpenCoven/.github", "", ["some drift"], dry_run=True)

        # The marker-bearing item is a pull request, so it must be excluded
        # from consideration entirely: no managed issue is found, and the
        # printed body is the freshly composed drift body (not a PATCH-style
        # reuse of the pull request), because dry-run never distinguishes
        # create/update — it always prints the computed body.
        self.assertIn(GOV.MANAGED_ISSUE_MARKER, out.getvalue())

    def test_readonly_scan_never_used_for_authenticated_dry_run(self) -> None:
        # An authenticated dry-run still has a token available and must
        # prefer the consistent GraphQL scan over the REST fallback.
        def fake_github_request(url, *, token=None, method="GET", payload=None):
            self.assertEqual(url, governance_cli.GRAPHQL_ENDPOINT, f"unexpected request: {method} {url}")
            return _gql_page([], has_next=False, end_cursor=None)

        with patch.object(governance_cli, "github_request", side_effect=fake_github_request) as mocked:
            with redirect_stdout(io.StringIO()):
                GOV.upsert_drift_issue("OpenCoven/.github", "token", ["some drift"], dry_run=True)

        self.assertEqual(len(_graphql_calls(mocked)), 1)

    def test_non_dry_run_without_token_rejected_by_command_reconcile(self) -> None:
        def fail_if_called(*_args, **_kwargs):
            self.fail("command_reconcile must return before any network call when token is missing and --dry-run is not set")

        args = argparse.Namespace(org="OpenCoven", repository="OpenCoven/.github", dry_run=False)
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(governance_cli, "fetch_public_repositories", side_effect=fail_if_called):
                with patch.object(governance_cli, "upsert_drift_issue", side_effect=fail_if_called):
                    result = GOV.command_reconcile(None, args)

        self.assertEqual(result, 2)

    def test_non_dry_run_without_token_rejected_by_upsert_drift_issue_defense_in_depth(self) -> None:
        # Even if upsert_drift_issue were reached directly with an empty
        # token and dry_run=False (bypassing the command_reconcile gate),
        # it must refuse to mutate rather than falling back to a scan that
        # cannot support a safe PATCH/POST.
        def fail_if_called(*_args, **_kwargs):
            self.fail("must fail closed before any network call")

        with patch.object(governance_cli, "github_request", side_effect=fail_if_called):
            with self.assertRaises(RuntimeError):
                GOV.upsert_drift_issue("OpenCoven/.github", "", ["some drift"], dry_run=False)


if __name__ == "__main__":
    unittest.main()
