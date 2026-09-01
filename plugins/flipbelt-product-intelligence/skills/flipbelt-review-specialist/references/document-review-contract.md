# Detail-page document review contract

Use this contract only for a FlipBelt detail-page wireframe, detail-page copy, or size-chart review. It defines comparison behavior and contains no product facts.

## Hard preflight and failure close

Before checking facts, confirm that all three read-only MCP tools are present and callable:

- `search_flipbelt_kb`
- `get_flipbelt_page`
- `get_flipbelt_asset`

Stop immediately when any tool is missing, MCP is unconfigured or disabled, authentication is absent/cancelled, a call returns 401/403/503, an identifier/page/asset is unavailable, or release metadata cannot be made consistent. Do not log in for the user or fall back to a local repository, archived knowledge, GitHub, browser portal, public web, fixture, Legacy snapshot, or model memory.

Use this response, naming the actual missing or failed item:

```text
当前无法执行 FlipBelt 详情页事实审查：本次 Codex 运行环境未提供完整可用的 FlipBelt 只读 MCP 工具集。缺失或失败项：<工具或状态>。我不会改用本地知识库、浏览器、公开网页或模型记忆。
```

## Inputs and source order

Identify the exact product name, season, market, artifact type, and requested scope. If the product is ambiguous, search for candidates and ask the user to choose; do not guess.

Apply this order:

1. The user's explicit correction in the current task for artifact identity and review scope.
2. The complete current-release Product Page for the exact product/season/market.
3. The exact same-release Size Guide for size, measurements, per-size storage, full specifications, or height/weight recommendations.
4. The current same-release Brand Base for brand, audience, product-line, or expression rules.
5. A published Reference/Entity Page or controlled Asset explicitly linked from the target page and applicable to the checked claim.

Search snippets locate pages but never prove a finding. Every evidence item must have `schema_version: 2.0` and the same `release_id` and `source_commit`. After a mismatch, re-read the entire evidence set once; if any mismatch remains, stop as Unknown without combining releases.

Only call `get_flipbelt_asset` when the artifact review needs an asset already referenced by the target page. Never expose object keys, credentials, or a permanent URL.

## Review dimensions

### Wireframe

- Required product definition, main features, construction, material/process, storage, use boundaries, and target-page priority are represented.
- Pocket/body-zone/temperature/scenario/gender branches and visual assets belong to the exact target product.
- No unsupported function, technology, asset, comparison, performance, or scenario is introduced.

### Detail-page copy

- Product identity, season/market, audience, product line, level, and use scenario match the current pages.
- Material name, composition, weight, structure, process, storage, reflectivity, colors, and launch claims retain the published scope.
- Test claims retain sample, color, material-versus-garment, method, conditions, qualifiers, and extrapolation boundaries.
- Brand spelling, positioning, audience relationships, product-line names, and expression boundaries match the current Brand Base.
- Similar styles, gender branches, seasons, or markets are not mixed.
- Absolute, medical, unsupported comparative, or internally sensitive statements are blocked.

### Size chart

- The exact `season + product_name + market` Size Guide is the only reference chart.
- Compare size labels, type codes, units, row/column meaning, ordering, ranges, full and detail-page measurements, fit/cut notes, gender applicability, storage details, and height/weight grid cells.
- Do not infer missing values, convert a similar product's chart, or silently resolve a boundary conflict.
- When two standardized JSON files are available, run `../scripts/compare_size_chart.ps1` with PowerShell 7 (`pwsh`) and include its deterministic findings as supporting evidence. The reference JSON must have been transcribed from the current MCP response; the script itself is not a fact source.

## Brand and sensitive-information gates

Check official spelling, positioning, core expression, audience relationships, product-line ownership, scenario/temperature boundaries, and limits on absolute claims against the current Brand Base.

External-facing content must not expose unpublished supplier or factory names, procurement information, production/report identifiers, internal codes, raw report or Tracking paths, credentials, tokens, authentication details, object-storage keys, or permanent asset URLs.

## Finding states

- `PASS`: the reviewed item agrees with the current evidence.
- `FAIL`: the reviewed item directly conflicts with current evidence.
- `MISSING`: a required or core item in current evidence is absent from the reviewed artifact.
- `NO-SOURCE`: the artifact makes a claim or includes a value/item for which the current release provides no applicable evidence.

Every non-PASS finding must identify the reviewed content, evidence page/section or explicit lack of source, the difference, and a correction recommendation. Do not use generic `revise`, `block`, or `unknown` labels inside this four-state report.

## Required report

```markdown
# 详情页审查报告

## 审查对象
- 产品：<产品名>
- 季节：<季节>
- 市场：<市场或未提供>
- 类型：<线框图/详情页/尺码表>
- 线上基准：<release_id>｜<source_commit 前 12 位>

## 摘要
- PASS：<N>
- FAIL：<N>
- MISSING：<N>
- NO-SOURCE：<N>

## 详细结果
### [状态] <检查项>
- 线上依据：<页面标题、段落及事实摘要，或当前 release 无依据>
- 被审查内容：<对应内容>
- 判定/差异：<结论>
- 建议修正：<仅 FAIL/MISSING/NO-SOURCE>

## 线上来源（当前激活 release）
- <页面标题>｜<source_path>
  release: <release_id>｜commit: <source_commit 前 12 位>

## 审批边界
- 本报告是自动审查建议，不是最终业务、产品、品牌、法律或人工批准。
```

Count every detailed finding exactly once. List only complete pages or controlled assets actually read and used. Use simplified Chinese and lead with the conclusion, then evidence.
