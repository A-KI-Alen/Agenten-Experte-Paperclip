# Paperclip Retrieval Guide

Der Spezialist laedt zuerst `SOURCE.md`, `SOURCES.md`, `TOPIC_MAP.md` und
`DOCS_INDEX.md`. Danach wird nur der relevante Ausschnitt aus offiziellen Quellen
oder dem privaten Volltext-Repo gelesen.

## Local Private Snapshot

```powershell
gh repo clone A-KI-Alen/Agenten-Experte-Paperclip-Private .cache/repos/Agenten-Experte-Paperclip-Private
rg -n "Heartbeat|adapter|workspace|approval|budget|PAPERCLIP_API_KEY" ".cache/repos/Agenten-Experte-Paperclip-Private/programs/paperclip/raw/Paperclip_Docu.md"
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
