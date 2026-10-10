# FlipBelt public plugin marketplace rules

- This repository is public. Never add credentials, tokens, cookies, private keys, employee data, production configuration, deployment scripts, or product knowledge content.
- Keep the repository limited to the four approved employee plugins: `flipbelt-product-intelligence`, `flipbelt-color-naming`, `design-seamless-patterns`, and `flipbelt-editorial-office` (approved on 2026-10-10).
- Product and brand facts must come from the authenticated read-only FlipBelt Knowledge app; plugin prose must not embed product facts.
- Keep `.agents/plugins/marketplace.json` as the marketplace source of truth.
- Every plugin must retain `.codex-plugin/plugin.json`; every skill must retain `SKILL.md`.
- Use strict semantic versions and review repository changes before merging because Workspace sync imports updates automatically.
- Treat the local-only `flipbelt-product-intelligence` repository as the sole editable source for Product Intelligence `shared/` and `skills/`. This public repository is a downstream distribution and must record the canonical source commit in `SOURCE-PROVENANCE.json`.
- Preserve the team-only plugin name, semantic version, `.app.json`, Workspace App reference, Marketplace manifest, public documentation, and validation adapters. Do not copy from the personal Marketplace or develop expert behavior directly here.
- Editorial Office is a downstream of the maintained personal plugin. Keep its eight role instructions and domain policies in that source; only adapt team connection, workspace discovery, validation, and delivery guidance here. Do not distribute internal term snapshots, machine paths, historical release identifiers, or privileged HTTP helpers. Record copied and adapted file hashes in the plugin's `SOURCE-PROVENANCE.json` and regenerate its contract after syncing.
- Run `python scripts/validate_marketplace.py`, the official plugin validator for all four plugins when available, and Skill quick validation before pushing. If the official plugin validator is absent, report that limitation and use the marketplace checks plus a read-only native Codex marketplace load; do not describe them as official schema validation.
