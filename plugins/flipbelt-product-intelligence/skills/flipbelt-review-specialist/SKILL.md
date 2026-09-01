---
name: flipbelt-review-specialist
description: Review FlipBelt detail-page wireframes, copy, size charts, product/material/brand claims, and evidence boundaries against the current published release. Use explicitly for structured document review; final approval remains with a human reviewer.
---

# FlipBelt Review Specialist

1. Read `../../shared/EXPERT-CONTRACT.md`, `../../shared/EVIDENCE-MODEL.md`, `../../shared/UNCERTAINTY-POLICY.md`, and `references/review-workflow.md`.
2. For a detail-page wireframe, detail-page copy, or size-chart review, also read and follow `references/document-review-contract.md` in full.
3. Before checking any FlipBelt fact, require all three read-only MCP tools: `search_flipbelt_kb`, `get_flipbelt_page`, and `get_flipbelt_asset`. If any tool is absent or returns an unavailable/authentication/authorization/service failure, stop with the contract's failure-close response. Do not fall back to local files, public web pages, model memory, fixtures, or Legacy snapshots.
4. Identify the exact product, season, market, artifact type, and requested scope. Search only to locate identifiers; read the complete Product Page and every Size Guide, Brand Base, or linked Reference Page actually used.
5. Lock every evidence response to one `schema_version`, `release_id`, and `source_commit`. Re-read the entire evidence set once after a mismatch; if it remains inconsistent, stop as Unknown.
6. Inventory each claim or required item as product, sizing, material, running, brand, dynamic, sensitive, or unsupported. Apply the responsible domain boundary without inventing a sibling expert result.
7. For document review, return only `PASS`, `FAIL`, `MISSING`, or `NO-SOURCE` per check and the exact report structure in the document review contract. For other claim review, return `pass`, `revise`, `block`, or `unknown` with rationale and required action.
8. When two standardized size-chart JSON files are available, use `scripts/compare_size_chart.ps1` as deterministic evidence. The script compares inputs only; it never supplies or replaces the authoritative Size Guide.

The result is an automated review recommendation. Never state that content has received final business, legal, product, brand, medical, or human approval.
