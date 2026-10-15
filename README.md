# FlipBelt Team Plugin Marketplace

FlipBelt 员工使用的 ChatGPT 与 Codex 插件分发仓库。仓库保持公开，以便 Workspace Marketplace 稳定读取和自动同步；公开仅代表源文件可见，不授予品牌、内容或代码的再使用许可。

## 包含的插件

- **FlipBelt Product Intelligence**：产品、尺码、材料、跑步、品牌与内容审查等八项专家能力；Review 支持线框图、详情页文案和尺码表的当前 release 四状态审查。需要员工本人连接 FlipBelt Knowledge。
- **FlipBelt 颜色命名**：为商品色卡、色彩企划与系列主题生成或审核中文颜色名。
- **无缝图案设计**：设计、修改、提示和分级验证四方连续纹样。
- **飞比特知识库编辑部**：总编、产品、尺码、扩展知识、专栏、关系台、独立审校和交付八项职责；通过现有 FlipBelt Knowledge 核对当前发布内容，制作修改单、草稿及审校材料。获授权的本地编辑需要实际知识工作区；正式发布仍走现有管理员流程。
- **FlipBelt AI 资产中心**：登记器梳理已有成果，孵化器探索工作需求；两个 Skill 共用资产中心的授权与版本确认规则。插件安装两项引导能力，连接器依赖见下文。

## AI 资产中心连接要求

`flipbelt-ai-asset-center` 当前以 Skills 加独立连接器依赖分发。可用连接器是 Windows 本机的受限 stdio MCP，提供 16 个工具；须在运行这些 Skills 的本地客户端单独安装、配置，并由使用者本人完成授权。具体要求见 [CONNECTORS.md](plugins/flipbelt-ai-asset-center/CONNECTORS.md)。

该资产连接器与 FlipBelt Knowledge App 是不同服务；当前没有可供此包引用的真实资产 Workspace App 或 HTTPS MCP。因此，团队市场收录、安装和静态校验不代表云端已经接通资产服务。云端连接与实际业务验收仍待真实资产 App 或 HTTPS MCP 和管理员配置；缺少工具时只能整理私有材料，不能声称已经保存或登记。

两项 Skill 从 AI 资产中心项目单向生成，来源提交、工作树状态及文件摘要见插件自己的 `SOURCE-PROVENANCE.json`。本仓不保存连接器实现、后端源码或凭据。

## 员工安装

1. 打开 ChatGPT 或 Codex 的“插件”。
2. 进入公司 Workspace 的插件列表。
3. 找到需要的 FlipBelt 插件并点击安装。
4. Product Intelligence 与知识库编辑部首次使用时，按提示使用本人员工身份连接 FlipBelt Knowledge。
5. 安装或更新后新建一个聊天再使用。

安装市场中的 Skill 不需要下载 ZIP 或安装 Codex CLI。AI 资产中心正式模式另需按其 CONNECTORS.md 准备 Windows 本机连接器；缺少连接器时保留本地整理模式。

## 管理员导入

在 **Admin > Plugins > Add > Import marketplace** 中填写：

- Source：`https://github.com/J21NIANYI/flipbelt-plugin-marketplace`
- Path：留空
- Branch：`main`

导入后逐个确认员工可见范围和安装策略。Marketplace 默认每日同步；需要立即拉取更新时，在 Marketplaces 中选择本仓库并点击 **Sync now**。

已导入本仓库的 Workspace 会在同步时获取新增插件，无需重复导入。新插件默认可安装，实际角色范围、安装策略和所需 App 由 Workspace 管理员核对；仓库策略字段不会覆盖后台策略。依据：[OpenAI 市场管理文档](https://learn.chatgpt.com/docs/enterprise/plugin-management)。

## 安全边界

- 本仓库不包含知识平台或资产中心后端源码、产品知识正文、员工数据、Cookie、Token、密钥、部署脚本或认证配置。
- Product Intelligence 与编辑部只引用现有 Workspace App；每位员工仍需独立完成 OAuth，安装插件不授予知识管理或发布权限。
- 所有产品事实仍由 FlipBelt Knowledge 的当前发布版本提供，插件文件本身不是产品事实源。

## 来源基线

Product Intelligence 的 `shared/` 与 `skills/` 从本地唯一真源 `flipbelt-product-intelligence@5eaf3f988d491e378cfe97ba5bad1a69ce80e09b` 单向同步，源版本为 `0.2.1`。本仓只保留团队插件名、分发 SemVer、Workspace `.app.json`、Marketplace 清单、公开说明和验证适配；完整来源与同步树摘要见 `SOURCE-PROVENANCE.json`。

编辑部团队版 `1.0.0` 从现有个人维护源 `flipbelt-editorial-office@0.1.0+codex.20260929070411` 单向分发。八项 Skill 入口及领域写作/审校规则保持原文；团队适配不包含内部术语库、本机凭据工具或历史发布快照。差异、来源哈希和更新方法见 [编辑部分发说明](plugins/flipbelt-editorial-office/README.md)。
