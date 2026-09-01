# FlipBelt public plugin marketplace rules

- This repository is public. Never add credentials, tokens, cookies, private keys, employee data, production configuration, deployment scripts, or product knowledge content.
- Keep the repository limited to the three approved employee plugins: `flipbelt-product-intelligence`, `flipbelt-color-naming`, and `design-seamless-patterns`.
- Product and brand facts must come from the authenticated read-only FlipBelt Knowledge app; plugin prose must not embed product facts.
- Keep `.agents/plugins/marketplace.json` as the marketplace source of truth.
- Every plugin must retain `.codex-plugin/plugin.json`; every skill must retain `SKILL.md`.
- Use strict semantic versions and review repository changes before merging because Workspace sync imports updates automatically.
- Run `python scripts/validate_marketplace.py`, the official plugin validator for all three plugins, and Skill quick validation before pushing.
