# FlipBelt Team Plugin Marketplace

FlipBelt 员工使用的 ChatGPT 与 Codex 插件分发仓库。仓库保持公开，以便 Workspace Marketplace 稳定读取和自动同步；公开仅代表源文件可见，不授予品牌、内容或代码的再使用许可。

## 包含的插件

- **FlipBelt Product Intelligence**：产品、尺码、材料、跑步、品牌与内容审查等八项专家能力；Review 支持线框图、详情页文案和尺码表的当前 release 四状态审查。需要员工本人连接 FlipBelt Knowledge。
- **FlipBelt 颜色命名**：为商品色卡、色彩企划与系列主题生成或审核中文颜色名。
- **无缝图案设计**：设计、修改、提示和分级验证四方连续纹样。

## 员工安装

1. 打开 ChatGPT 或 Codex 的“插件”。
2. 进入公司 Workspace 的插件列表。
3. 找到需要的 FlipBelt 插件并点击安装。
4. Product Intelligence 首次使用时，按提示使用本人员工身份连接 FlipBelt Knowledge。
5. 安装或更新后新建一个聊天再使用。

员工不需要下载 ZIP，也不需要安装 Codex CLI。

## 管理员导入

在 **Admin > Plugins > Add > Import marketplace** 中填写：

- Source：`https://github.com/J21NIANYI/flipbelt-plugin-marketplace`
- Path：留空
- Branch：`main`

导入后逐个确认员工可见范围和安装策略。Marketplace 默认每日同步；需要立即拉取更新时，在 Marketplaces 中选择本仓库并点击 **Sync now**。

## 安全边界

- 本仓库不包含知识平台源码、产品知识正文、员工数据、Cookie、Token、密钥、部署脚本或认证配置。
- Product Intelligence 只引用现有 Workspace App；每位员工仍需独立完成 OAuth。
- 所有产品事实仍由 FlipBelt Knowledge 的当前发布版本提供，插件文件本身不是产品事实源。
