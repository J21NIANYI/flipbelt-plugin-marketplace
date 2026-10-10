# 生产契约与运行时复查
## 证据与三层边界
获授权的实际知识工作区中，完整主库为 content/v2/full。线上活动发布投影：Page/Search/MCP 共用 current_release_id。GitHub 软件与治理仓库不自动代表当前线上正文。
每次涉及线上基线时，只读查询 https://wiki.flipbeltchina.com/api/v1/ready 与 https://wiki.flipbeltchina.com/release-meta.json，记录时间、release_id、source_kind、source_ref、source_commit、content_set_sha256、content_source_mode 和内容开关。不得读取凭据或登录真实业务角色进行自动验收。
应用 source_commit 用于定位当前已部署代码；online release 的 source_commit 仅追溯 Schema/规则/Builder，不是该在线正文的 Git 提交。source_kind 与 content_source_mode 分别表示活动 release 来源和运行策略，不能混同。
两者不一致时明确报告过渡状态：可继续只读分析、逐页对账与修改单；不得宣称迁移完成或自行切换策略。不能因 M2M 关闭否定已启用的 Web 发布。

## 当前基线
不分发历史 release、应用提交或开关值快照。每次使用实时只读响应与同一 release 的目标页面记录基线；拿不到状态时如实标记未核对。

## 能力与交付
单页“编辑正文 → 发布修改”由 KB_ADMIN 使用现有 Web Session、CSRF 和近期认证，追加 Revision、生成完整候选并 CAS 激活；不部署应用。保存草稿不发布，不能把草稿保存和发布修改写成同一行为。
“知识管理 → 批量发布”接受平台现有 V2 Release ZIP，先预检新增/覆盖/不变及路径，人工确认后发布；缺少页面不等于删除。不得发明 Editorial Import Package、reference_manifest 或自定义导入协议。
只有用户明确要求 ZIP 交付时才构建 ZIP；先核对当前知识构建工具及生产导入 Schema、哈希、Reference/Asset 契约。脚本可验证和打包已逐页编辑的对象，不得生成或重写知识页面正文。无法确认契约则只交付可审阅变更与缺口。
管理员 Snapshot 下载用于基线比对与恢复辅助，不自动覆盖主库。Revision 差异/恢复、批量移动/停用、素材目录按实际部署能力提供人工操作材料；历史恢复会形成新发布，停用需明确授权，均不得作为只读动作执行。
PR/Proposal 回流保留为兼容和明确指定的 Git 路径，不是在线发布的必经步骤。Local Publisher、M2M、来源策略切换不得顺带启用。
所有真实业务操作与最终验收由用户或指定人员执行。自动检查只提供验证材料；功能已存在不等于本次已操作或验收通过。

## 动态 HTML 能力核对
[动态契约](dynamic-html.md) 对应 2026-09-29 的平台本地实现，不据日期推断生产已部署。线上使用还需由有权限的操作者核对 HTML contract 1.0、实际发布可用状态和精确已部署应用；API 与 Nginx HTML frame CSP 须一起适配。纯本地制作不联网。现有 Web 发布是内容激活，应用部署另行授权；本插件不代替用户登录、真实角色操作或最终验收。旧应用回滚先冻结内容写入，保留 HTML 数据和当前知识指针。
