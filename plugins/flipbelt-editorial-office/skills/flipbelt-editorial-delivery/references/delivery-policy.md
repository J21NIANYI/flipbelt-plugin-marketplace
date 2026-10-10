# 交付流程
## 交付状态
READY_FOR_EDIT：精确修改单已完成，仍待指定执行者编辑。
READY_FOR_REVIEW：本地变更及规定检查完成，附独立审校结果/剩余人工复核。
NEEDS_REVISION：有可修正错误；BLOCKED：基线冲突、缺依赖或来源阻断。
这些仅为内部状态，不映射为平台状态；knowledge_status published 不等于线上发布。现有 V2 Release ZIP 与自定义编辑包不同，按生产契约核对，不能再宣称平台没有 ZIP 导入能力。
## L1 修改单
列页面 ID/标题、Section/位置、原文、新文、来源及条件、Reference 变化、影响范围、基线哈希、建议执行路径。不自行宣称后台现状或当前原文；先读取目标。
用户要求本地改动时遵循领域编辑，不强迫走在线路径。若走在线编辑，按已核对的 Web 直接发布路径准备人工操作材料；PR 回流仅为兼容路径。
## 本地交付
列精确文件、create/update/unchanged、来源摘要、实际差异、Reference 报告、审校与验证结果、未解决项。不把内部来源路径或报告加入知识 release。
不构建自定义 Editorial Import Package、reference_manifest 或新平台状态。用户明确请求 ZIP 时遵循 [生产契约](../../flipbelt-editorial-chief/references/production-contract.md) 中现有 V2 Release ZIP 规则；仅按 [fbkb 操作契约](../../flipbelt-editorial-chief/references/knowledge-operations.md)，在已有认证可用且用户明确授权对应目标时提交 Revision；不自行启用 Publisher M2M，不切换内容真源或激活 Release。
## 兼容回流（仅明确选择该路径时）
在线 Revision JSON PR 包先使用：
```powershell
python tools/kb_content_publisher.py validate-pr-bundle <bundle.json> --candidate-out <知识根外新候选路径> --preview-out <知识根外预览路径>
```
根据工具输出 target_path 定位唯一 Page；独立核对来源/差异后逐页编辑。候选不是知识真源，下载/校验不是发布。
旧 proposal：
```powershell
python tools/kb_release.py apply-proposal <proposal.zip> --dry-run
```
conflict 停止；无冲突且用户授权应用时，遵循仓库逐页正文规则，不能以旧工具存在绕过当前禁止脚本改写正文的要求。
## 发布边界
默认依据 [生产契约](../../flipbelt-editorial-chief/references/production-contract.md) 区分本地主库与线上活动内容。现有 Web 发布不要求先回流 Git；Git 发布只用于明确选择且仍受支持的兼容路径。提交、推送、生产触发均须已有明确授权；不自动写数据库/OSS，不原位修改 release。
旧 release 再激活只能走 activate_existing，并提供目标 release 与精确预期当前 release；对象完整性、竞态和 ready 失败保持/恢复原 release。此为边界说明，不在本插件自动执行。
当前无 V2→钉钉受控同步契约，不能使用旧 V1 archive 或旧块级同步流程。收到同步请求先报告适配缺口，不能直接写远端。

交付单独报告：本地变更、草稿/Revision、预检/候选、线上活动 release、自动验证、人工验收。没有实际证据的阶段写未执行；不得将源码构建、ZIP 预检或 READY 候选当作发布成功。
