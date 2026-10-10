# 动态 HTML 发布交付

先读 [动态 HTML 契约](../../flipbelt-editorial-chief/references/dynamic-html.md) 和 [生产契约](../../flipbelt-editorial-chief/references/production-contract.md)。本流程准备真实可上传文件与操作材料，不授予远程提交、内容激活或应用部署权限。会话已有明确授权时按范围继续，不重复询问。

## 发布步骤

1. 交付经独立审校的单篇 HTML；记录 Page/Section ID、原文件 SHA、候选 SHA、修改摘要、目录路径、来源与实际基线版本。使用 [交付记录模板](../templates/html-handoff.md)。用户要求确认后导出时须等待该确认。
2. 上线使用前，由有权限的操作者确认已部署 HTML contract 1.0，API 与 Nginx frame 策略同时具备。通过实际平台界面核对 HTML 发布可用后才可进入 Web 发布；自动只读状态不替代人的业务/视觉验收。
3. 由管理员上传完成当前平台的服务器预检，校验真实 base_version、引用与分组；团队包不含远程预检 helper，不为此启用 M2M。预检通过不代表 Revision 已提交或 Release 已激活。
4. 用户本人登录现有 KB_ADMIN 入口，在“知识管理 → 新增”选择 HTML 或文章“编辑正文 → 上传/替换 HTML”，检查 manifest 身份、目录和预览。新页 base_version=0；已有页沿用服务器读取的当前版本，409 先逐页对账，不能提升版本强行覆盖。
5. “保存草稿”仅保存草稿；“发布新知识/发布修改”沿用 CSRF、近期认证、幂等键及内容开关，创建 Revision、完整候选并 CAS 激活。请求结果不明时先核对实际版本，不擅自重复发布。服务端提示近期认证过期时由用户重新认证，保留工作文件。
6. 记录实际 Revision、候选及活动 release_id/content_set_sha256，再由人工确认交互正文、文字版、目录跳转、搜索/MCP 与窄屏效果。缺失服务端字段标记“未返回”，不能编造哈希。激活失败时保留原 current_release_id，结果不明时写“待核对”。

## 恢复与回滚

历史恢复通过已有管理员入口创建新 Revision/Release；恢复后实际核对 HTML 和 Markdown。Snapshot 中的 HTML 与 SHA 用于比对，不能据此自动覆盖正式知识库。有 HTML 的 Active Release Recovery 使用 1.2，保留原包、摘要与兼容工具；恢复只允许明确隔离空数据库，不提供生产 HTTP 导入恢复接口。
应用回滚另行授权。回滚到旧应用前先关闭三个内容写入/激活开关，只读保留知识 release、HTML 数据和新增列；旧发布器不能继续写入。回到支持 HTML 的版本、核对快照/摘要后再按既有授权恢复写入。文章回滚与应用回滚是不同动作。

## 状态报告

分别报告：制品已生成、离线格式验证、服务器预检、草稿保存、Revision 提交、Release 激活、人工验收。没有实际回执就不写“已发布”。本轮仅更新插件能力不意味着文章上线或生产平台部署。
