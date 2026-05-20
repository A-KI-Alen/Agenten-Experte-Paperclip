# Paperclip Topic Map

Routing-Werkzeug fuer CEO, Collector und Paperclip Specialist.

| Topic | Headings | Activation terms |
| --- | ---: | --- |
| `activity_debugging` | 37 | run transcript, activity log, failed runs, troubleshooting and diagnostics |
| `adapters_runtime` | 63 | adapter types, local/remote invocation, heartbeat model, runtime errors |
| `agents_org` | 159 | companies, CEO, agents, hiring, org structure, skills and instructions |
| `api_cli` | 89 | Paperclip API, CLI, curl examples, webhooks and automation |
| `approvals_governance` | 35 | approval queue, strategy approvals, hire approvals, board override powers |
| `costs_budgets` | 58 | cost ledger, budgets, provider/biller/finance tabs, spend control |
| `data_export` | 16 | exports, audit traces, remote sync and data lifecycle |
| `general` | 754 | general Paperclip concepts and uncategorized docs |
| `installation_deployment` | 65 | install, server deployment, systemd, nginx, docker, database setup |
| `issues_workflow` | 80 | issues, task lifecycle, comments, status changes, inbox and checkout patterns |
| `plugins_mcp` | 29 | plugin SDK, MCP server, skills and tool integration |
| `security_secrets` | 33 | secrets, API keys, JWTs, bearer tokens, authentication and redaction |
| `workspaces_execution` | 44 | execution workspaces, worktrees, GitHub credentials, PR/code workflows |

## Escalation Flow

1. Debugger arbeitet zwei echte Runs autonom.
2. Wenn nicht geloest: Debugger uebergibt komprimierte Lage an CEO.
3. CEO aktiviert Paperclip Specialist plus ggf. GitHub/npm/runtime Spezialisten.
4. Paperclip Specialist recherchiert read-only in Doku, Code, Issues, PRs und npm.
5. Collector synthetisiert Expertenantworten mit Logs und Debug-Kontext.
6. Debugger setzt den Fix direkt mit Write-Access um und testet.
