# 检查命令
先按 [fbkb 操作契约](../../flipbelt-editorial-chief/references/knowledge-operations.md) 核对安装与合同；常规 Page 检查自动使用统一入口，独立审校保持只读。以下补充检查从知识仓根执行，解释目的并记录实际结果。
V2 变更：
```powershell
& <已确认的fbkb入口> validate --json
python tools/kb_audit.py --input content/v2/full --skill-root <已确认的插件根>/skills/flipbelt-editorial-chief
git diff --check
git diff -- <目标文件>
```
Preview 必须显式指向本次 content/v2/full 或目标候选，不使用默认 representative 输入。先核对 kb_preview_v2.py 的 --input、--out、--evidence 参数，输出到受控知识根以外的内部目录；工具输出不是知识真源。
根据变更运行 tests 中相应 Schema、size、taxonomy、audit、column 测试；独立人工来源/数值审查不能由这些检查代替。
仅 release 链路变更再做全库 validate、真实 build、release validate、相关完整测试与 workflow 语法检查，并证明失败不切换当前 release。按 README 的固定命令在全新空目录构建。
旧 validate_product_page.ps1、validate_size_page.ps1 和迁移/生成正文脚本不进入 V2 日常检查链。不得因名字含 audit/content/phase5 就默认工具只读；先查写入行为。
插件实现检查使用插件 validate_plugin.py、Skill quick_validate.py、跨链接/依赖/包哈希与真实行为场景；这些不证明平台已发布。

编辑部规则完整性使用 Chief 的 editorial-contract.json（生成的文件哈希清单），不是内容 Schema。领域规则只在个人维护源修改并刷新其清单；团队分发从市场仓根运行 `python -X utf8 scripts/sync_editorial.py --source <已确认的个人编辑部插件根>`，保留审阅后的团队适配，再校验、审查差异和发布。哈希校验不代替语义审校。

云端没有实际工作区/工具时，依据原稿、当前页面和差异审校，未执行的 Schema、Audit、Preview 或 CLI 项标为 NOT_CHECKED，不能用文本检查冒充通过。
