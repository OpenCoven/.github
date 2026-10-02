#!/usr/bin/env python3
"""Validate, generate, and reconcile the OpenCoven public governance plane.

The deterministic validation/generation path uses only the Python standard
library and performs no network access. GitHub reconciliation is an explicit,
separate command intended for the scheduled least-privilege workflow.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# Re-export the public validation surface used by repository tests and adopters.
from governance_core import (  # noqa: E402,F401
    ROOT, expanded_repositories, validate_exception_data,
    validate_initiative_data, validate_manifest_data, validate_registry_data,
    resolve_trusted_target_file, validate_reusable_invocation,
)
from governance_model import Governance  # noqa: E402,F401
from governance_cli import (  # noqa: E402,F401
    GRAPHQL_BOT_LOGIN, GRAPHQL_BOT_TYPENAME, MANAGED_ISSUE_AUTHOR,
    MANAGED_ISSUE_MARKER, MANAGED_ISSUE_TITLE, command_reconcile,
    fetch_open_issues, fetch_open_issues_readonly, find_managed_drift_issue,
    main, reconcile_public_inventory, upsert_drift_issue,
)

if __name__ == "__main__":
    raise SystemExit(main())
