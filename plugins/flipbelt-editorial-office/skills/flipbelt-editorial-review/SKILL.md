---
name: flipbelt-editorial-review
description: Independently review FlipBelt editorial changes for evidence, semantics, V2 structure, references and domain rules; select risk-appropriate checks and report review status without publishing.
---

# 飞比特编辑审校

先读 [共同约束](../flipbelt-editorial-chief/references/workspace-contract.md)、[审校流程](references/review-policy.md)。
独立审校者使用目标差异、原始来源、对象依赖和适用规则，不拿作者结论当证据。使用只读独立 Agent；工具不可用时明确待人工独立复核，不能用作者自查代替。
按对象加载 [产品](references/product-checks.md)、[尺码](references/size-checks.md)、[扩展](references/extended-checks.md)、[专栏](references/column-checks.md)，执行 [检查命令](references/validation.md) 中适用项。
报告 FACT、STRUCTURE、REFERENCE、DUPLICATION、BRAND_LANGUAGE、SOURCE 各 PASS/WARNING/FAIL，逐项附对象、证据、问题和修正建议；只有实际检查才能 PASS。
审校只读，不修正文；作者修正后只复核变动及受影响项。
动态 HTML 同时加载 [HTML 检查](references/html-checks.md)，核对全部状态与 Markdown、缩进/短标题、图表去重、资源和沙箱边界；自动验证与人工验收分别记录。

## 本地统一入口
涉及本地编辑、检查或 Revision 交付时，读取 [fbkb 操作契约](../flipbelt-editorial-chief/references/knowledge-operations.md)；遵循本职责的自动检查与授权边界。
