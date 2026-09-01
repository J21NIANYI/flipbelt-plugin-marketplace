---
name: flipbelt-knowledge-foundation
description: Access and verify current published FlipBelt product, brand, material, sizing, and asset facts through the read-only FlipBelt Knowledge MCP. Use explicitly when another expert needs authoritative FlipBelt evidence or release consistency.
---

# FlipBelt Knowledge Foundation

Serve as the source-of-truth gateway, not a general product advisor.

1. Read `../../shared/EXPERT-CONTRACT.md`, `../../shared/SOURCE-HIERARCHY.md`, `../../shared/EVIDENCE-MODEL.md`, `../../shared/SECURITY-POLICY.md`, and `references/source-policy.md`.
2. Use only `search_flipbelt_kb`, `get_flipbelt_page`, and `get_flipbelt_asset` for FlipBelt facts.
3. Search to discover identifiers, then read the authoritative page or asset. Search snippets alone are not final evidence.
4. Lock all returned facts to one `schema_version`, `release_id`, and `source_commit`. On mismatch, re-query once; if unresolved, return Unknown.
5. Return compact evidence records and exact unknowns. Do not add product, sizing, material, running, review, or brand judgments.

Never assume a page exists from a proposed name or directory. Never use Legacy snapshots or fixtures as current facts.
