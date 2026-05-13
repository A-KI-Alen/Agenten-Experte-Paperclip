# Agenten-Experte-Paperclip

Public Paperclip expert knowledge pack for A-KI program specialists.

This repository prepares Paperclip source metadata, routing indexes and
read-only retrieval instructions for a Paperclip specialist agent.

The full transformed `Paperclip_Docu.md` crawl is intentionally not included in
this public repository because the current official Paperclip documentation is
licensed under CC BY-NC-ND 4.0. The public repo records hashes, source state,
headings and retrieval instructions. The full local snapshot can be used
privately for internal RAG/debugging.

## What Is Included

```text
programs/paperclip/
  profile.toml              # Paperclip specialist profile
  SOURCES.md                # researched official/secondary sources
  SOURCE.md                 # local snapshot metadata and publication rule
  DOCS_INDEX.md             # heading-only index from private snapshot
  TOPIC_MAP.md              # CEO/Collector routing map
  RETRIEVAL.md              # read-only retrieval guide
  state/
    source_state.json       # private snapshot hash/stats
    upstream_state.json     # public upstream source baseline
scripts/
  build_paperclip_specialist_pack.py
  check_paperclip_sources.py
```

## Primary Sources

- https://github.com/paperclipai/paperclip
- https://github.com/paperclipai/paperclip-docs
- https://docs.paperclip.ing/
- https://paperclip.ing/docs

Additional secondary sources are listed in `programs/paperclip/SOURCES.md`.

## Update Policy

The workflow `Paperclip Source Sync` runs roughly twice per month. It compares
Paperclip code, docs, website and npm package state against the stored baseline.

If public sources changed, the workflow opens an issue requesting a local
refresh of the private `Paperclip_Docu.md` snapshot and regenerated specialist
index. The public repo does not auto-commit a modified full-text docs crawl.

## Licensing

- Paperclip software sources are MIT licensed.
- Current Paperclip documentation sources are CC BY-NC-ND 4.0.
- A-KI helper scripts and metadata are MIT licensed.

See `LICENSE.md`, `NOTICE.md` and `LICENSES/`.
