# Paperclip Topic Map

Routing-Werkzeug fuer CEO, Collector und Paperclip Specialist.

| Topic | Headings | Activation terms |
| --- | ---: | --- |
| `activity_debugging` | 28 | run transcript, activity log, failed runs, troubleshooting and diagnostics |
| `adapters_runtime` | 46 | adapter types, local/remote invocation, heartbeat model, runtime errors |
| `agents_org` | 131 | companies, CEO, agents, hiring, org structure, skills and instructions |
| `api_cli` | 62 | Paperclip API, CLI, curl examples, webhooks and automation |
| `approvals_governance` | 34 | approval queue, strategy approvals, hire approvals, board override powers |
| `costs_budgets` | 34 | cost ledger, budgets, provider/biller/finance tabs, spend control |
| `data_export` | 13 | exports, audit traces, remote sync and data lifecycle |
| `general` | 487 | general Paperclip concepts and uncategorized docs |
| `installation_deployment` | 48 | install, server deployment, systemd, nginx, docker, database setup |
| `issues_workflow` | 63 | issues, task lifecycle, comments, status changes, inbox and checkout patterns |
| `plugins_mcp` | 15 | plugin SDK, MCP server, skills and tool integration |
| `security_secrets` | 26 | secrets, API keys, JWTs, bearer tokens, authentication and redaction |
| `workspaces_execution` | 28 | execution workspaces, worktrees, GitHub credentials, PR/code workflows |

## Escalation Flow

1. Debugger arbeitet zwei echte Runs autonom.
2. Wenn nicht geloest: Debugger uebergibt komprimierte Lage an CEO.
3. CEO aktiviert Paperclip Specialist plus ggf. GitHub/npm/runtime Spezialisten.
4. Paperclip Specialist recherchiert read-only in Doku, Code, Issues, PRs und npm.
5. Collector synthetisiert Expertenantworten mit Logs und Debug-Kontext.
6. Debugger setzt den Fix direkt mit Write-Access um und testet.
