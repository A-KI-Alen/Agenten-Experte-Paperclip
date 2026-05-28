#!/usr/bin/env python3
"""Check public Paperclip source state for changes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


DEFAULT_STATE = Path("programs/paperclip/state/upstream_state.json")
DEFAULT_REPORT = Path("reports/paperclip-update-check.md")

REPOS: dict[str, str] = {
    "paperclip_repo": "paperclipai/paperclip",
    "paperclip_docs_repo": "paperclipai/paperclip-docs",
    "paperclip_legacy_docs_repo": "paperclipai/docs",
    "paperclip_website_repo": "paperclipai/paperclip-website",
    "hermes_adapter_repo": "paperclipai/hermes-paperclip-adapter",
    "companies_repo": "paperclipai/companies",
    "companies_tool_repo": "paperclipai/companies-tool",
    "pr_reviewer_repo": "paperclipai/pr-reviewer",
    "clipmart_repo": "paperclipai/clipmart",
    "org_profile_repo": "paperclipai/.github",
}

SITES: dict[str, str] = {
    "docs_site": "https://docs.paperclip.ing/",
    "main_docs_entry": "https://paperclip.ing/docs",
}

NPM_PACKAGES: tuple[str, ...] = (
    "paperclipai",
    "@paperclipai/server",
    "@paperclipai/plugin-sdk",
    "@paperclipai/mcp-server",
    "@paperclipai/ui",
    "@paperclipai/db",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def request_bytes(url: str) -> bytes:
    headers = {
        "User-Agent": "A-KI Agenten-Experte-Paperclip Sync/1.0",
        "Accept": "application/json,text/html,text/plain,*/*",
    }
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        return response.read()


def request_json(url: str) -> dict[str, Any]:
    return json.loads(request_bytes(url).decode("utf-8"))


def latest_commit(repo: str) -> str:
    """Return latest default-branch commit SHA for a GitHub repo.

    Prefer GitHub API (optionally authenticated). Fall back to `git ls-remote`
    against the public HTTPS remote to avoid unauthenticated API rate limits.
    """

    try:
        payload = request_json(f"https://api.github.com/repos/{repo}")
        branch = payload["default_branch"]
        commit = request_json(f"https://api.github.com/repos/{repo}/commits/{branch}")
        return commit["sha"]
    except (HTTPError, URLError, TimeoutError, KeyError):
        # Fallback: use the remote's advertised HEAD (default branch).
        # Example output:
        #   <sha>\tHEAD
        output = subprocess.check_output(
            ["git", "ls-remote", f"https://github.com/{repo}.git", "HEAD"],
            text=True,
            encoding="utf-8",
            timeout=30,
        ).strip()
        if not output:
            raise
        sha = output.split()[0]
        if len(sha) < 40:
            raise RuntimeError(f"Unexpected ls-remote output for {repo}: {output!r}")
        return sha


def site_fingerprint(url: str) -> str:
    return hashlib.sha256(request_bytes(url)).hexdigest()


def npm_version(package: str) -> str:
    package_url = quote(package, safe="@")
    payload = request_json(f"https://registry.npmjs.org/{package_url}/latest")
    return payload["version"]


def collect_state() -> dict[str, Any]:
    state: dict[str, Any] = {
        "checked_utc": utc_now(),
        "repos": {},
        "sites": {},
        "npm": {},
    }
    for key, repo in REPOS.items():
        try:
            state["repos"][key] = {"repo": repo, "latest_commit": latest_commit(repo)}
        except (HTTPError, URLError, TimeoutError, KeyError) as exc:
            state["repos"][key] = {"repo": repo, "error": str(exc)}
    for key, url in SITES.items():
        try:
            state["sites"][key] = {"url": url, "sha256": site_fingerprint(url)}
        except (HTTPError, URLError, TimeoutError) as exc:
            state["sites"][key] = {"url": url, "error": str(exc)}
    for package in NPM_PACKAGES:
        try:
            state["npm"][package] = {"version": npm_version(package)}
        except (HTTPError, URLError, TimeoutError, KeyError) as exc:
            state["npm"][package] = {"error": str(exc)}
    return state


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def diff_state(stored: dict[str, Any], latest: dict[str, Any], compare_site_fingerprints: bool = False) -> list[str]:
    reasons: list[str] = []
    for key, item in latest.get("repos", {}).items():
        old = stored.get("repos", {}).get(key, {})
        if old.get("latest_commit") and item.get("latest_commit") and old.get("latest_commit") != item.get("latest_commit"):
            reasons.append(f"{item['repo']} commit changed.")
        elif item.get("error"):
            reasons.append(f"{item['repo']} check failed: {item['error']}")
    for key, item in latest.get("sites", {}).items():
        old = stored.get("sites", {}).get(key, {})
        if (
            compare_site_fingerprints
            and old.get("sha256")
            and item.get("sha256")
            and old.get("sha256") != item.get("sha256")
        ):
            reasons.append(f"{item['url']} fingerprint changed.")
        if item.get("error"):
            reasons.append(f"{item['url']} check failed: {item['error']}")
    for package, item in latest.get("npm", {}).items():
        old = stored.get("npm", {}).get(package, {})
        if old.get("version") and item.get("version") and old.get("version") != item.get("version"):
            reasons.append(f"npm package {package} version changed.")
        elif item.get("error"):
            reasons.append(f"npm package {package} check failed: {item['error']}")
    return reasons


def write_report(path: Path, stored: dict[str, Any], latest: dict[str, Any], reasons: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Paperclip Source Update Check",
        "",
        f"- Checked UTC: `{utc_now()}`",
        f"- Update needed: `{str(bool(reasons)).lower()}`",
        "",
        "## Reasons",
        "",
    ]
    lines.extend(f"- {reason}" for reason in (reasons or ["No upstream changes detected."]))
    lines.extend(["", "## Stored State", "", "```json", json.dumps(stored, indent=2, ensure_ascii=False), "```", ""])
    lines.extend(["## Latest State", "", "```json", json.dumps(latest, indent=2, ensure_ascii=False), "```", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_github_output(values: dict[str, str]) -> None:
    output_path = os.getenv("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--refresh-state", action="store_true")
    parser.add_argument(
        "--compare-site-fingerprints",
        action="store_true",
        help="Also treat rendered docs-site fingerprint changes as update triggers. Disabled by default because the site can emit dynamic HTML.",
    )
    args = parser.parse_args()

    stored = load_state(args.state)
    latest = collect_state()
    reasons = [] if args.refresh_state else diff_state(stored, latest, args.compare_site_fingerprints)

    if args.refresh_state:
        write_json(args.state, latest)
        stored = latest

    write_report(args.report, stored, latest, reasons)
    write_github_output({"update_needed": str(bool(reasons)).lower()})
    print(f"update_needed={str(bool(reasons)).lower()}")
    for reason in reasons:
        print(f"- {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
