#!/usr/bin/env python3
"""Build a public Paperclip specialist pack from a private local docs snapshot.

The current Paperclip docs are CC BY-NC-ND 4.0. This generator therefore does
not publish the transformed full-text crawl. It records source metadata, hashes,
headings, routing topics and read-only retrieval instructions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


HEADING_RE = re.compile(r"^(?P<level>#{1,6})\s+(?P<title>.+?)\s*$")


@dataclass(frozen=True)
class Heading:
    line: int
    level: int
    title: str
    topic: str


TOPIC_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("installation_deployment", ("installation", "install", "deploy", "server", "nginx", "https", "systemd", "docker", "database")),
    ("agents_org", ("agent", "agents", "company", "org", "ceo", "hire", "instructions", "skills")),
    ("issues_workflow", ("issue", "issues", "task", "inbox", "comment", "checkout", "workflow")),
    ("approvals_governance", ("approval", "approve", "strategy", "governance", "board override")),
    ("costs_budgets", ("cost", "budget", "spend", "provider", "biller", "finance")),
    ("activity_debugging", ("activity", "debug", "transcript", "logs", "troubleshooting", "failed run", "error")),
    ("adapters_runtime", ("adapter", "claude", "codex", "openclaw", "opencode", "pi_local", "heartbeat", "invoke")),
    ("api_cli", ("api", "cli", "endpoint", "curl", "paperclipai", "webhook")),
    ("workspaces_execution", ("workspace", "worktree", "github token", "execution", "repo", "pull request")),
    ("plugins_mcp", ("plugin", "mcp", "model context protocol", "skill")),
    ("security_secrets", ("secret", "api key", "token", "jwt", "password", "auth", "security")),
    ("data_export", ("export", "data lifecycle", "remote sync", "trace")),
)

TOPIC_TRIGGERS: dict[str, str] = {
    "installation_deployment": "install, server deployment, systemd, nginx, docker, database setup",
    "agents_org": "companies, CEO, agents, hiring, org structure, skills and instructions",
    "issues_workflow": "issues, task lifecycle, comments, status changes, inbox and checkout patterns",
    "approvals_governance": "approval queue, strategy approvals, hire approvals, board override powers",
    "costs_budgets": "cost ledger, budgets, provider/biller/finance tabs, spend control",
    "activity_debugging": "run transcript, activity log, failed runs, troubleshooting and diagnostics",
    "adapters_runtime": "adapter types, local/remote invocation, heartbeat model, runtime errors",
    "api_cli": "Paperclip API, CLI, curl examples, webhooks and automation",
    "workspaces_execution": "execution workspaces, worktrees, GitHub credentials, PR/code workflows",
    "plugins_mcp": "plugin SDK, MCP server, skills and tool integration",
    "security_secrets": "secrets, API keys, JWTs, bearer tokens, authentication and redaction",
    "data_export": "exports, audit traces, remote sync and data lifecycle",
    "general": "general Paperclip concepts and uncategorized docs",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def classify(title: str) -> str:
    haystack = title.lower()
    for topic, needles in TOPIC_RULES:
        if any(needle in haystack for needle in needles):
            return topic
    return "general"


def parse_headings(text: str) -> list[Heading]:
    headings: list[Heading] = []
    in_fence = False
    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if not match:
            continue
        title = match.group("title").strip().strip("#").strip()
        level = len(match.group("level"))
        headings.append(Heading(line=idx, level=level, title=title, topic=classify(title)))
    return headings


def grouped(headings: Iterable[Heading]) -> dict[str, list[Heading]]:
    result: dict[str, list[Heading]] = {}
    for heading in headings:
        result.setdefault(heading.topic, []).append(heading)
    return dict(sorted(result.items(), key=lambda item: item[0]))


def toml_list(values: Iterable[str]) -> str:
    return "[" + ", ".join(f'"{value}"' for value in values) + "]"


def write_profile(out_dir: Path) -> None:
    (out_dir / "profile.toml").write_text(
        '''id = "paperclip-specialist"
name = "Paperclip Specialist"
type = "program-specialist"
permissions = "READ_ONLY"
source_docs = ["private-local:Paperclip_Docu.md", "https://docs.paperclip.ing/", "https://paperclip.ing/docs"]
entrypoints = ["SOURCE.md", "DOCS_INDEX.md", "TOPIC_MAP.md", "RETRIEVAL.md", "SOURCES.md"]
knowledge_layers = [
  "docs_rag_private: lokaler Paperclip_Docu.md Snapshot fuer internen Retrieval-Kontext",
  "docs_public: offizielle Paperclip-Dokuquellen und Docs-Repositories",
  "code_read: read-only Quellcode-Recherche im Hauptrepo fuer Stacktraces, Services, API, UI und DB",
  "issue_pr_read: read-only GitHub-Issue-/PR-Recherche fuer neue, ungeloeste oder schlecht dokumentierte Bugs",
  "npm_release_read: read-only Abgleich von CLI/Server/Plugin-Paketen und Release-Versionen",
  "local_context: Paperclip-Runs, Agentenprofile, Issues, Logs und bisherige Debugger-Runs aus A-KI"
]

[[repository_sources]]
id = "paperclipai/paperclip"
role = "application-code-source"
access = "READ_ONLY"
use_for = ["core code", "server", "ui", "cli", "packages", "issues", "pull requests", "release workflows"]

[[repository_sources]]
id = "paperclipai/paperclip-docs"
role = "official-documentation-source"
access = "READ_ONLY"
use_for = ["canonical docs", "docs source", "docs issues", "docs diffs"]

[[repository_sources]]
id = "paperclipai/docs"
role = "legacy-or-secondary-documentation-source"
access = "READ_ONLY"
use_for = ["historical docs", "API/deploy/adapters references", "cross-checks"]

[[repository_sources]]
id = "paperclipai/paperclip-website"
role = "website-source"
access = "READ_ONLY"
use_for = ["landing page context", "public positioning", "docs entrypoints"]

[[repository_sources]]
id = "paperclipai/hermes-paperclip-adapter"
role = "adapter-source"
access = "READ_ONLY"
use_for = ["Hermes adapter", "external adapter behavior", "integration examples"]

[[repository_sources]]
id = "paperclipai/companies"
role = "company-template-source"
access = "READ_ONLY"
use_for = ["company templates", "agent org examples"]

[[repository_sources]]
id = "paperclipai/companies-tool"
role = "company-tool-source"
access = "READ_ONLY"
use_for = ["npx companies tool", "template install behavior"]

activation = """
Der CEO aktiviert diesen Spezialisten, wenn ein Issue nach zwei echten Debugger-Runs
nicht geloest ist und Hinweise auf Paperclip, Agents, Companies, Heartbeats,
Approvals, Issues, Workspaces, Adapter, MCP, Plugins, Budgets, CLI, API, Server,
UI oder Deployment enthaelt. Der Spezialist analysiert read-only und nimmt keine
Aenderungen an Paperclip, Tickets, Dateien, Workflows, Services oder GitHub vor.
"""

answer_contract = [
  "Kurzdiagnose",
  "Getrennte Evidenz: Doku, Code, Issues/PRs, NPM/Release und lokaler A-KI-Kontext",
  "Relevante Doku-/Index-Stellen mit Abschnitt und Quelle",
  "Relevante Code-/Issue-/PR-Treffer mit Repo, Pfad oder Link und Status",
  "Wahrscheinlichste Ursache",
  "Welche Evidenz fehlt noch",
  "Konkrete Checks fuer Collector oder Debugger",
  "Sicherer Fix-Pfad fuer den Debugger",
  "Risiken/Rollback-Hinweise",
  "Ob weitere Spezialisten benoetigt werden"
]

stop_rules = [
  "Keine Secrets oder personenbezogenen Rohdaten anfordern oder ausgeben",
  "Keine produktiven Aenderungen selbst ausfuehren",
  "Keine GitHub-Issues kommentieren, schliessen oder veraendern",
  "Keine Pull Requests oder Branches selbst erstellen",
  "CC BY-NC-ND Doku nicht veraendern oder als abgeleiteten Volltext oeffentlich republizieren",
  "Bei Datenbank-/Migrationsthemen Backup-, Staging- und Rollback-Frage markieren"
]
''',
        encoding="utf-8",
    )


def write_sources(out_dir: Path, source_meta: dict[str, object]) -> None:
    (out_dir / "SOURCES.md").write_text(
        """# Paperclip Sources

## Primary Official Sources

- `paperclipai/paperclip`: main MIT-licensed application repo, code, issues, PRs, releases, workflows.
- `paperclipai/paperclip-docs`: current documentation source for `https://docs.paperclip.ing/`, licensed CC BY-NC-ND 4.0.
- `https://docs.paperclip.ing/`: current public documentation site.
- `https://paperclip.ing/docs`: docs entrypoint linked from the main app README.

## Secondary Official Sources

- `paperclipai/docs`: older/secondary MIT-licensed docs repository.
- `paperclipai/paperclip-website`: website source and public positioning.
- `paperclipai/hermes-paperclip-adapter`: Hermes adapter source.
- `paperclipai/companies`: example company/template source.
- `paperclipai/companies-tool`: npx companies tool source.

## Package/Release Sources

- `paperclipai` on npm: CLI package.
- `@paperclipai/server` on npm: server package.
- `@paperclipai/plugin-sdk`, `@paperclipai/mcp-server`, `@paperclipai/ui`, `@paperclipai/db`, adapter and plugin packages on npm.

## Community/Live Debug Signals

- `paperclipai/paperclip` issues, pull requests and discussions.
- Discord and social links are community signals only; do not ingest or quote private/non-public content.

## Local Snapshot

The local `Paperclip_Docu.md` snapshot was used to generate this public index.
The full transformed snapshot is intentionally not stored in this public repo
because the current Paperclip documentation license is CC BY-NC-ND 4.0.

```json
""" + json.dumps(source_meta, indent=2, ensure_ascii=False) + """
```
""",
        encoding="utf-8",
    )


def write_index(out_dir: Path, headings: list[Heading]) -> None:
    lines = [
        "# Paperclip Docs Index",
        "",
        "- Full transformed local docs snapshot is not vendored in this public repo.",
        "- Line numbers refer to the private local `Paperclip_Docu.md` snapshot described in `SOURCES.md`.",
        "- Use this index to select topics, then read official docs/code/issue sources read-only.",
        "",
    ]
    for topic, topic_headings in grouped(headings).items():
        lines.extend([f"## {topic}", ""])
        for heading in topic_headings:
            indent = "  " * max(0, heading.level - 1)
            lines.append(f"{indent}- L{heading.line}: H{heading.level} {heading.title}")
        lines.append("")
    (out_dir / "DOCS_INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def write_topic_map(out_dir: Path, headings: list[Heading]) -> None:
    groups = grouped(headings)
    lines = [
        "# Paperclip Topic Map",
        "",
        "Routing-Werkzeug fuer CEO, Collector und Paperclip Specialist.",
        "",
        "| Topic | Headings | Activation terms |",
        "| --- | ---: | --- |",
    ]
    for topic, topic_headings in groups.items():
        lines.append(f"| `{topic}` | {len(topic_headings)} | {TOPIC_TRIGGERS.get(topic, '')} |")
    lines.extend(
        [
            "",
            "## Escalation Flow",
            "",
            "1. Debugger arbeitet zwei echte Runs autonom.",
            "2. Wenn nicht geloest: Debugger uebergibt komprimierte Lage an CEO.",
            "3. CEO aktiviert Paperclip Specialist plus ggf. GitHub/npm/runtime Spezialisten.",
            "4. Paperclip Specialist recherchiert read-only in Doku, Code, Issues, PRs und npm.",
            "5. Collector synthetisiert Expertenantworten mit Logs und Debug-Kontext.",
            "6. Debugger setzt den Fix direkt mit Write-Access um und testet.",
            "",
        ]
    )
    (out_dir / "TOPIC_MAP.md").write_text("\n".join(lines), encoding="utf-8")


def write_retrieval(out_dir: Path) -> None:
    (out_dir / "RETRIEVAL.md").write_text(
        """# Paperclip Retrieval Guide

Der Spezialist laedt zuerst `SOURCE.md`, `SOURCES.md`, `TOPIC_MAP.md` und
`DOCS_INDEX.md`. Danach wird nur der relevante Ausschnitt aus offiziellen Quellen
oder dem privaten lokalen Snapshot gelesen.

## Local Private Snapshot

```powershell
rg -n "Heartbeat|adapter|workspace|approval|budget|PAPERCLIP_API_KEY" "<local-private-path>\\Paperclip_Docu.md"
```

Der private Snapshot darf fuer internes RAG/Debugging genutzt werden, wird aber
nicht als veraenderter Volltext oeffentlich publiziert.

## Official Docs

```powershell
gh repo clone paperclipai/paperclip-docs .cache/repos/paperclip-docs
rg -n "Heartbeat|adapter|workspace|approval|budget" .cache/repos/paperclip-docs/docs
```

## Code Search

```powershell
gh repo clone paperclipai/paperclip .cache/repos/paperclip
rg -n "<stacktrace-or-symbol>" .cache/repos/paperclip
rg -n "PAPERCLIP_AGENT_JWT_SECRET|PAPERCLIP_API_KEY|heartbeat|approval|workspace" .cache/repos/paperclip
```

## Issues, PRs, Discussions

```powershell
gh issue list -R paperclipai/paperclip --state all --search "<stacktrace-or-error-fragment>"
gh pr list -R paperclipai/paperclip --state all --search "<symbol-or-error-fragment>"
gh search issues "<stacktrace-or-error-fragment> repo:paperclipai/paperclip" --state all
```

For GitHub Discussions, use browser or GraphQL read-only search if the issue/PR
search does not explain the failure.

## npm/Release Signals

```powershell
npm view paperclipai version license repository.url
npm view @paperclipai/server version license repository.url
npm search paperclipai --json
```

## Antwortdisziplin

- Doku-, Code-, Issue-/PR-, npm- und lokalen A-KI-Kontext getrennt ausweisen.
- Keine Secrets, Tokens, Chat-IDs oder echte Kundendaten ausgeben.
- Bei CC BY-NC-ND Doku keine langen Passagen kopieren und keine abgeleiteten Volltexte oeffentlich erzeugen.
- Issue-/PR-Treffer mit Repo, Titel, Status und Link nennen; keine Tickets veraendern.
- Bei mehreren beteiligten Systemen weitere Spezialisten nennen, z.B. GitHub, n8n, Docker, Node.js, PostgreSQL oder OAuth.
""",
        encoding="utf-8",
    )


def write_source(out_dir: Path, source_meta: dict[str, object]) -> None:
    (out_dir / "SOURCE.md").write_text(
        """# Paperclip Specialist Source

- Program: Paperclip
- Public source of truth: official Paperclip repos and docs sites listed in `SOURCES.md`.
- Private retrieval source: local `Paperclip_Docu.md` snapshot, hash recorded below.
- Permission model: read-only specialist knowledge. Fixes are implemented by the Debugger, not by the specialist.
- Publication rule: do not store the transformed Paperclip docs full text in this public repo while docs are CC BY-NC-ND 4.0.

## Snapshot Metadata

```json
""" + json.dumps(source_meta, indent=2, ensure_ascii=False) + """
```
""",
        encoding="utf-8",
    )


def write_state(out_dir: Path, source_meta: dict[str, object]) -> None:
    state_dir = out_dir / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "source_state.json").write_text(
        json.dumps(source_meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def source_meta(source: Path, text: str, headings: list[Heading]) -> dict[str, object]:
    stat = source.stat()
    return {
        "program": "paperclip",
        "local_snapshot_name": "Paperclip_Docu.md",
        "local_snapshot_publication": "not_included_due_to_CC_BY_NC_ND_docs_license",
        "local_snapshot_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "local_snapshot_bytes": stat.st_size,
        "local_snapshot_last_write_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "generated_utc": utc_now(),
        "heading_count": len(headings),
        "top_level_heading_count": sum(1 for heading in headings if heading.level == 1),
        "line_count": text.count("\n") + 1,
        "word_count": len(re.findall(r"\S+", text)),
        "docs_license": "CC BY-NC-ND 4.0 for paperclipai/paperclip-docs documentation",
        "code_license": "MIT for paperclipai/paperclip software",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output-root", default=Path("programs"), type=Path)
    parser.add_argument("--slug", default="paperclip")
    args = parser.parse_args()

    source = args.source.resolve()
    if not source.exists():
        raise SystemExit(f"Source not found: {source}")

    text = source.read_text(encoding="utf-8")
    headings = parse_headings(text)
    if not headings:
        raise SystemExit("No markdown headings found.")

    out_dir = (args.output_root / args.slug).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = source_meta(source, text, headings)

    write_profile(out_dir)
    write_sources(out_dir, meta)
    write_source(out_dir, meta)
    write_index(out_dir, headings)
    write_topic_map(out_dir, headings)
    write_retrieval(out_dir)
    write_state(out_dir, meta)

    print(f"Generated Paperclip specialist pack at {out_dir}")
    print(f"Headings indexed: {len(headings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
