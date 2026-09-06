"""CLI and explicit network reconciliation for the OpenCoven governance plane."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

from governance_core import ROOT, validate_reusable_invocation
from governance_model import Governance

def github_request(url: str, *, token: str | None = None, method: str = "GET", payload: dict[str, Any] | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "OpenCoven-governance-reconciler/1",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read()
            return json.loads(content) if content else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {url} failed: HTTP {exc.code}: {detail[:500]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub API {method} {url} failed: {exc}") from exc


def fetch_public_repositories(org: str, token: str | None) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    page = 1
    while True:
        query = urllib.parse.urlencode({"type": "public", "per_page": 100, "page": page})
        batch = github_request(f"https://api.github.com/orgs/{urllib.parse.quote(org)}/repos?{query}", token=token)
        if not isinstance(batch, list):
            raise RuntimeError("unexpected GitHub repository response")
        result.extend(item for item in batch if item.get("visibility", "public") == "public" and not item.get("private", False))
        if len(batch) < 100:
            break
        page += 1
    return result


def reconcile_public_inventory(governance: Governance, live: list[dict[str, Any]]) -> list[str]:
    declared = governance.registry_map()
    actual = {item["name"]: item for item in live}
    drift: list[str] = []
    for name in sorted(set(actual) - set(declared), key=str.lower):
        drift.append(f"unregistered public repository: `{name}`")
    for name in sorted(set(declared) - set(actual), key=str.lower):
        drift.append(f"registered repository not present in live public inventory: `{name}`")
    for name in sorted(set(declared) & set(actual), key=str.lower):
        expected = declared[name]["observed"]
        observed = actual[name]
        if declared[name]["observation_status"] != "verified-public":
            drift.append(
                f"`{name}` observation status mismatch: "
                f"registry={declared[name]['observation_status']} live=verified-public"
            )
        if bool(observed.get("archived")) != expected.get("archived"):
            drift.append(f"`{name}` archived mismatch: registry={expected.get('archived')} live={bool(observed.get('archived'))}")
        if observed.get("default_branch") != expected.get("default_branch"):
            drift.append(f"`{name}` default branch mismatch: registry=`{expected.get('default_branch')}` live=`{observed.get('default_branch')}`")
    return drift


MANAGED_ISSUE_MARKER = "<!-- opencoven-governance-drift:v1 -->"
MANAGED_ISSUE_TITLE = "[governance-drift] Public repository registry drift"
MANAGED_ISSUE_AUTHOR = "github-actions[bot]"

# GitHub's two APIs report the scheduled Actions bot's identity differently:
# REST (`user.login`) reports the suffixed form `github-actions[bot]`
# (`MANAGED_ISSUE_AUTHOR` above), while GraphQL's `author` union reports the
# unsuffixed login `github-actions` together with `__typename: Bot`. These
# constants are that exact GraphQL identity pair; only this exact pair is
# normalized to the canonical `MANAGED_ISSUE_AUTHOR` login used by
# `find_managed_drift_issue`. A login of `github-actions` under any other
# `__typename` (for example a `User` or `Mannequin` that happens to share
# the name) is a distinct identity and must never be implicitly trusted.
GRAPHQL_BOT_TYPENAME = "Bot"
GRAPHQL_BOT_LOGIN = "github-actions"

GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
MAX_ISSUE_SCAN_PAGES = 500  # safety bound: 500 * 100 = 50,000 open issues per scan

ISSUES_QUERY = """
query($owner: String!, $repo: String!, $after: String) {
  repository(owner: $owner, name: $repo) {
    issues(first: 100, states: OPEN, orderBy: {field: CREATED_AT, direction: ASC}, after: $after) {
      pageInfo { hasNextPage endCursor }
      nodes { id number title body author { __typename login } }
    }
  }
}
"""


def _fail_closed(owner: str, repo: str, reason: str) -> "RuntimeError":
    return RuntimeError(f"refusing to continue open-issue scan for {owner}/{repo}: {reason}")


def _validate_issue_node(node: Any, *, owner: str, repo: str, index: int) -> dict[str, Any]:
    if not isinstance(node, dict):
        raise _fail_closed(owner, repo, f"node[{index}] is not an object")
    node_id = node.get("id")
    number = node.get("number")
    title = node.get("title")
    body = node.get("body")
    if not isinstance(node_id, str) or not node_id:
        raise _fail_closed(owner, repo, f"node[{index}].id is missing or malformed")
    if not isinstance(number, int):
        raise _fail_closed(owner, repo, f"node[{index}].number is missing or malformed")
    if not isinstance(title, str):
        raise _fail_closed(owner, repo, f"node[{index}].title is missing or malformed")
    if body is not None and not isinstance(body, str):
        raise _fail_closed(owner, repo, f"node[{index}].body is malformed")
    author = node.get("author")
    login = None
    if author is not None:
        if not isinstance(author, dict):
            raise _fail_closed(owner, repo, f"node[{index}].author is malformed")
        login = author.get("login")
        typename = author.get("__typename")
        if login is not None and not isinstance(login, str):
            raise _fail_closed(owner, repo, f"node[{index}].author.login is malformed")
        if typename is not None and not isinstance(typename, str):
            raise _fail_closed(owner, repo, f"node[{index}].author.__typename is malformed")
        # Normalize *only* the exact GraphQL Actions-bot identity
        # (__typename == "Bot", login == "github-actions") to the canonical
        # REST-style login `find_managed_drift_issue` trusts. Any other
        # __typename/login combination — including a non-Bot author whose
        # login happens to equal "github-actions" — is left exactly as
        # GitHub reported it, so it can never be conflated with the real
        # bot identity by that downstream comparison.
        if typename == GRAPHQL_BOT_TYPENAME and login == GRAPHQL_BOT_LOGIN:
            login = MANAGED_ISSUE_AUTHOR
    return {"id": node_id, "number": number, "title": title, "body": body or "", "login": login}


def _validate_issues_page(response: Any, *, owner: str, repo: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not isinstance(response, dict):
        raise _fail_closed(owner, repo, "GraphQL response is not an object")
    errors = response.get("errors")
    if errors:
        raise _fail_closed(owner, repo, f"GraphQL returned errors: {errors}")
    data = response.get("data")
    if not isinstance(data, dict):
        raise _fail_closed(owner, repo, "GraphQL response is missing `data`")
    repository = data.get("repository")
    if not isinstance(repository, dict):
        raise _fail_closed(owner, repo, "GraphQL repository lookup is missing or inaccessible")
    issues = repository.get("issues")
    if not isinstance(issues, dict):
        raise _fail_closed(owner, repo, "GraphQL response is missing the issues connection")
    page_info = issues.get("pageInfo")
    if not isinstance(page_info, dict) or not isinstance(page_info.get("hasNextPage"), bool):
        raise _fail_closed(owner, repo, "GraphQL response has a malformed pageInfo")
    end_cursor = page_info.get("endCursor")
    if end_cursor is not None and not isinstance(end_cursor, str):
        raise _fail_closed(owner, repo, "GraphQL response has a malformed endCursor")
    nodes = issues.get("nodes")
    if not isinstance(nodes, list):
        raise _fail_closed(owner, repo, "GraphQL response has malformed issue nodes")
    validated = [_validate_issue_node(node, owner=owner, repo=repo, index=index) for index, node in enumerate(nodes)]
    return page_info, validated


def fetch_open_issues(owner: str, repo: str, token: str) -> list[dict[str, Any]]:
    """Fetch every open issue via GraphQL cursor pagination in stable creation order.

    This is the mutation-capable scan: it requires an authenticated token and
    is the only scan path `upsert_drift_issue` uses when it is about to PATCH
    or POST. (Tokenless read-only reporting must use
    `fetch_open_issues_readonly` instead — see that function's docstring for
    why the two paths have different consistency guarantees.)

    REST page-number pagination is unsafe over a mutable open-issue
    collection: a `page=N` request is an absolute offset into whatever set
    of open issues matches *at request time*, so if an earlier issue closes
    between two page requests, every later issue shifts left by one. That
    shift can make the managed issue vanish entirely if it was about to
    cross the page boundary, or return a boundary issue on both pages.

    GraphQL connection cursors identify a position relative to the
    already-returned node rather than an absolute offset. Traversing in
    ascending creation order also means a newly created issue always sorts
    after every already-fetched page (creation time only increases), so it
    cannot retroactively appear on, or invalidate, a page already fetched.
    This does not make the multi-request scan atomic — GitHub offers no
    atomic "list open issues" snapshot — but it removes the specific
    shift-based skip/duplicate failure mode of offset pagination.

    Every response shape is validated explicitly (`_validate_issues_page`,
    `_validate_issue_node`), issue nodes are deduplicated by their immutable
    GraphQL node id, and any malformed or inconsistent shape (missing
    pageInfo, `hasNextPage: true` without an `endCursor`, a cursor repeated
    without forward progress, a duplicate node id across pages, or a
    malformed node) fails closed with `RuntimeError` instead of silently
    returning a partial, skipped, or duplicated result.
    """
    if not token:
        raise RuntimeError(
            f"fetch_open_issues (GraphQL) requires an authenticated token for {owner}/{repo}; "
            "tokenless callers must use fetch_open_issues_readonly for read-only reporting"
        )
    result: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_cursors: set[str] = set()
    cursor: str | None = None
    for page in range(1, MAX_ISSUE_SCAN_PAGES + 1):
        response = github_request(
            GRAPHQL_ENDPOINT,
            token=token,
            method="POST",
            payload={"query": ISSUES_QUERY, "variables": {"owner": owner, "repo": repo, "after": cursor}},
        )
        page_info, nodes = _validate_issues_page(response, owner=owner, repo=repo)
        for node in nodes:
            if node["id"] in seen_ids:
                raise _fail_closed(
                    owner, repo,
                    f"GraphQL returned duplicate issue node id {node['id']!r} across pages, "
                    "which indicates the open-issue collection was not traversed consistently",
                )
            seen_ids.add(node["id"])
            result.append(node)
        if not page_info["hasNextPage"]:
            return result
        end_cursor = page_info.get("endCursor")
        if not end_cursor:
            raise _fail_closed(owner, repo, "hasNextPage=true was reported without an endCursor")
        if end_cursor in seen_cursors:
            raise _fail_closed(
                owner, repo,
                "GraphQL returned a repeated pagination cursor, which indicates the open-issue "
                "collection is not being traversed consistently",
            )
        seen_cursors.add(end_cursor)
        cursor = end_cursor
    raise _fail_closed(owner, repo, f"exceeded {MAX_ISSUE_SCAN_PAGES} pages without reaching the end of the connection")


def fetch_open_issues_readonly(owner: str, repo: str, token: str | None) -> list[dict[str, Any]]:
    """Read-only REST scan of open issues, for tokenless dry-run reporting only.

    `--dry-run` is documented to work without `GITHUB_TOKEN` (unauthenticated
    scheduled/local observation), but the GraphQL scan in `fetch_open_issues`
    always requires a token — the unauthenticated GraphQL endpoint rejects or
    aggressively rate-limits token-less requests, which previously broke the
    tokenless dry-run contract outright. This function restores that
    contract using ordinary REST `page=N` offset pagination instead.

    Offset pagination over a mutable collection can, in principle, skip or
    double-report an issue near a page boundary if the open-issue set
    changes between page requests (see `fetch_open_issues`'s docstring for
    the full failure mode). That weakness is acceptable *only* here because
    this function is used exclusively for read-only, best-effort dry-run
    reporting: `upsert_drift_issue` never calls `_patch_issue` or POSTs a
    new issue on this path, so an offset shift here cannot itself create a
    duplicate issue or apply a stale mutation — at worst the printed dry-run
    report under- or over-counts a boundary issue, which is an observational
    accuracy tradeoff, not a state-mutation correctness one. This function
    must never be used when a run is going to mutate GitHub state.
    """
    result: list[dict[str, Any]] = []
    for page in range(1, MAX_ISSUE_SCAN_PAGES + 1):
        query = urllib.parse.urlencode({"state": "open", "per_page": 100, "page": page})
        batch = github_request(f"https://api.github.com/repos/{owner}/{repo}/issues?{query}", token=token or None)
        if not isinstance(batch, list):
            raise _fail_closed(owner, repo, "unexpected GitHub issues response: expected a JSON list")
        for index, item in enumerate(batch):
            if not isinstance(item, dict):
                raise _fail_closed(owner, repo, f"issues response item[{index}] is not an object")
            if "pull_request" in item:
                continue  # the REST /issues endpoint also returns pull requests
            number = item.get("number")
            title = item.get("title")
            body = item.get("body")
            if not isinstance(number, int) or not isinstance(title, str):
                raise _fail_closed(owner, repo, f"issues response item[{index}] is missing number/title")
            if body is not None and not isinstance(body, str):
                raise _fail_closed(owner, repo, f"issues response item[{index}].body is malformed")
            user = item.get("user")
            login = user.get("login") if isinstance(user, dict) else None
            result.append({"id": f"rest:{number}", "number": number, "title": title, "body": body or "", "login": login})
        if len(batch) < 100:
            return result
    raise _fail_closed(owner, repo, f"exceeded {MAX_ISSUE_SCAN_PAGES} pages without reaching the end of open issues")


def find_managed_drift_issue(issues: list[dict[str, Any]], *, marker: str, title: str) -> dict[str, Any] | None:
    """Locate the single managed drift issue, failing closed on ambiguity or spoofing.

    An issue is trusted as "the" managed issue only when it carries the exact
    managed title and marker and was authored by the scheduled workflow's bot
    identity (compared as the canonical `MANAGED_ISSUE_AUTHOR` login).
    `issues` must already be normalized to the flattened
    `{id, number, title, body, login}` shape produced by either
    `fetch_open_issues` (GraphQL) or `fetch_open_issues_readonly` (REST).
    REST reports that identity natively as `github-actions[bot]`; GraphQL
    reports it as the unsuffixed login `github-actions` with
    `author.__typename == "Bot"`, so `_validate_issue_node` normalizes only
    that exact `(__typename, login)` pair to `MANAGED_ISSUE_AUTHOR` before
    this function ever sees it — a differently-typed author whose login
    happens to be `github-actions` is left untouched and therefore compares
    unequal here, exactly like any other untrusted author. Both scans also
    exclude pull requests before returning, so no separate
    not-a-pull-request check is needed here. Any other open issue that
    merely contains the marker text is treated as a spoof/ambiguity signal:
    automated action is refused rather than silently picking a candidate or
    creating a duplicate.
    """
    trusted: list[dict[str, Any]] = []
    suspicious: list[dict[str, Any]] = []
    for item in issues:
        if marker not in (item.get("body") or ""):
            continue
        is_trusted = item.get("title") == title and item.get("login") == MANAGED_ISSUE_AUTHOR
        (trusted if is_trusted else suspicious).append(item)
    if suspicious:
        numbers = ", ".join(f"#{item.get('number')}" for item in suspicious)
        raise RuntimeError(
            "refusing to create or update the managed drift issue: found untrusted issue(s) "
            f"carrying the governance-drift marker ({numbers}); resolve manually before the "
            "observer can proceed"
        )
    if len(trusted) > 1:
        numbers = ", ".join(f"#{item.get('number')}" for item in trusted)
        raise RuntimeError(
            f"refusing to act: found multiple managed drift issues ({numbers}); resolve the "
            "ambiguity manually"
        )
    return trusted[0] if trusted else None


def _patch_issue(owner: str, repo: str, number: int, token: str, payload: dict[str, Any]) -> None:
    github_request(f"https://api.github.com/repos/{owner}/{repo}/issues/{number}", token=token, method="PATCH", payload=payload)


def upsert_drift_issue(repository: str, token: str, drift: list[str], *, dry_run: bool) -> None:
    marker = MANAGED_ISSUE_MARKER
    title = MANAGED_ISSUE_TITLE
    owner, repo = repository.split("/", 1)

    if not dry_run and not token:
        # Defense in depth: `command_reconcile` already refuses to reach
        # this function without a token unless `--dry-run` is set, but this
        # function itself must never PATCH/POST without a token regardless
        # of caller. Failing closed here keeps that contract even if this
        # function is invoked directly (as the test suite does).
        raise RuntimeError(
            "refusing to mutate GitHub issues without a token; reconcile-github requires "
            "GITHUB_TOKEN unless --dry-run is used"
        )

    # Route the scan by authentication, not by dry_run: an authenticated
    # dry-run still uses the consistent GraphQL cursor scan (it has a token
    # available), while a tokenless run is only ever reachable in dry-run
    # mode (enforced above) and must fall back to the reduced-consistency
    # REST scan documented on `fetch_open_issues_readonly`.
    issues = fetch_open_issues(owner, repo, token) if token else fetch_open_issues_readonly(owner, repo, token)
    existing = find_managed_drift_issue(issues, marker=marker, title=title)
    if drift:
        body = "\n".join([
            marker,
            "# Public repository registry drift",
            "",
            "The scheduled read-only observer found differences between `governance/repositories.json` and GitHub's public repository metadata.",
            "",
            *[f"- {item}" for item in drift],
            "",
            "This issue is a coordination signal only. It does not authorize archive, transfer, visibility, deletion, release, publication, or protected OpenCoven state changes.",
            "",
            f"Observed at: `{datetime.utcnow().replace(microsecond=0).isoformat()}Z`",
        ])
        if dry_run:
            print(body)
            return
        if existing:
            _patch_issue(owner, repo, existing["number"], token, {"title": title, "body": body})
            return
        # Final revalidation immediately before POST: the initial scan and
        # this creation call are not atomic, and GitHub does not offer a
        # compare-and-swap "create issue only if absent" primitive. Without
        # this second scan, a managed issue created concurrently by another
        # reconciler run between the initial scan and this POST would be
        # duplicated. This narrows the race window rather than eliminating
        # it, and it fails closed (via `find_managed_drift_issue`) instead of
        # proceeding if the revalidation scan itself is ambiguous or
        # malformed.
        revalidation_issues = fetch_open_issues(owner, repo, token)
        revalidated_existing = find_managed_drift_issue(revalidation_issues, marker=marker, title=title)
        if revalidated_existing:
            _patch_issue(owner, repo, revalidated_existing["number"], token, {"title": title, "body": body})
        else:
            github_request(f"https://api.github.com/repos/{owner}/{repo}/issues", token=token, method="POST", payload={"title": title, "body": body})
    elif existing:
        if dry_run:
            print(f"would close clean drift issue #{existing['number']}")
        else:
            _patch_issue(owner, repo, existing["number"], token, {"state": "closed", "state_reason": "completed"})


def command_validate(governance: Governance, _: argparse.Namespace) -> int:
    errors = governance.validate()
    if errors:
        print("Governance validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Governance validation passed.")
    return 0


def command_generate(governance: Governance, args: argparse.Namespace) -> int:
    if args.check:
        errors = governance.validate_generated()
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print("Generated governance views are current.")
        return 0
    governance.generate()
    print("Generated governance views updated.")
    return 0


def command_validate_manifest(governance: Governance, args: argparse.Namespace) -> int:
    if args.local_self_declared_repository and os.environ.get("GITHUB_ACTIONS") == "true":
        print("--local-self-declared-repository is forbidden in GitHub Actions", file=sys.stderr)
        return 2
    errors = governance.validate_manifest_file(
        Path(args.target_root),
        args.path,
        caller_repository=args.caller_repository,
        allow_self_declared_repository=args.local_self_declared_repository,
    )
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Agent manifest valid: {args.path}")
    return 0


def command_validate_evidence(governance: Governance, args: argparse.Namespace) -> int:
    errors = governance.validate_evidence_file(Path(args.target_root), args.path)
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Evidence packet valid: {args.path}")
    return 0


def command_validate_reusable_invocation(_: Governance, args: argparse.Namespace) -> int:
    errors = validate_reusable_invocation(
        Path(args.target_root),
        caller_workflow_ref=args.caller_workflow_ref,
        caller_repository=args.caller_repository,
        policy_ref=args.policy_ref,
        reusable_workflow=args.reusable_workflow,
        path_input_name=args.path_input_name,
        runtime_path=args.runtime_path,
        default_runtime_path=args.default_runtime_path,
    )
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Reusable workflow invocation valid.")
    return 0


def command_reconcile(governance: Governance, args: argparse.Namespace) -> int:
    token = os.environ.get("GITHUB_TOKEN")
    if not args.dry_run and not token:
        print("GITHUB_TOKEN is required unless --dry-run is used", file=sys.stderr)
        return 2
    live = fetch_public_repositories(args.org, token)
    drift = reconcile_public_inventory(governance, live)
    if args.repository:
        upsert_drift_issue(args.repository, token or "", drift, dry_run=args.dry_run)
    if drift:
        print("Public repository drift detected:", file=sys.stderr)
        for item in drift:
            print(f"- {item}", file=sys.stderr)
        return 1
    print(f"Public repository inventory reconciled: {len(live)} repositories.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="validate authoritative records, workflows, and generated views")
    generate = sub.add_parser("generate", help="generate deterministic public views")
    generate.add_argument("--check", action="store_true", help="fail when generated files are stale")
    manifest = sub.add_parser("validate-manifest", help="validate a repository agent manifest against the public registry when present")
    manifest.add_argument("--target-root", default=".", help="trusted checkout root that contains the repository-relative manifest path")
    manifest.add_argument("--caller-repository", help="actual GitHub caller repository in owner/name form")
    manifest.add_argument(
        "--local-self-declared-repository",
        action="store_true",
        help="local-only safe mode: use manifest.repository.name for registry lookup after trusted path checks",
    )
    manifest.add_argument("path")
    evidence = sub.add_parser("validate-evidence", help="validate a governance evidence packet")
    evidence.add_argument("--target-root", default=".", help="trusted checkout root that contains the repository-relative evidence path")
    evidence.add_argument("path")
    reusable = sub.add_parser("validate-reusable-invocation", help="validate a direct caller job for an OpenCoven reusable workflow")
    reusable.add_argument("--target-root", required=True)
    reusable.add_argument("--caller-workflow-ref", required=True)
    reusable.add_argument("--caller-repository", required=True)
    reusable.add_argument("--policy-ref", required=True)
    reusable.add_argument("--reusable-workflow", required=True)
    reusable.add_argument("--path-input-name", required=True)
    reusable.add_argument("--runtime-path", required=True)
    reusable.add_argument("--default-runtime-path")
    reconcile = sub.add_parser("reconcile-github", help="compare public registry with live GitHub public repository metadata")
    reconcile.add_argument("--org", default="OpenCoven")
    reconcile.add_argument("--repository", default="OpenCoven/.github", help="repository used for the deduplicated drift issue")
    reconcile.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    governance = Governance(ROOT)
    handlers = {
        "validate": command_validate,
        "generate": command_generate,
        "validate-manifest": command_validate_manifest,
        "validate-evidence": command_validate_evidence,
        "validate-reusable-invocation": command_validate_reusable_invocation,
        "reconcile-github": command_reconcile,
    }
    return handlers[args.command](governance, args)
