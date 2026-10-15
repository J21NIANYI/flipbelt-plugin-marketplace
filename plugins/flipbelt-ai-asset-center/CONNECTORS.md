# 资产中心连接器配置

本插件使用资产中心受限连接器，不是只读 FlipBelt Knowledge App。当前没有可供本包引用的已验证资产 Workspace App 标识或远程 MCP 地址。

## 已有能力

当前适配器为 Windows 本机 Python stdio MCP。它连接 `https://jtzhzt.flipbeltchina.com` 的受限业务 API；该网址和 `/api/v1/agent` 都不是远程 MCP 入口，不能填入 HTTP MCP 地址栏。身份由服务端校验，本人设备授权产生的凭据仅在本机由 DPAPI 加密保存，禁止打入安装包或共用企业令牌。

Python 要求为 3.11–3.13；依赖以随附锁文件为准。连接器源自正式工程的 `connector/`，独立版本与源码哈希见连接器来源清单。千问 ZIP 带该目录；Codex 市场包需从同次千问分发 ZIP 中提取 `connector/` 到本人选定的 Windows 目录，或使用已核验的正式工程 connector。不要把本机开发者的安装路径发给全员。

## Windows 本机准备

先安装 Python 和 uv，再在用户选定目录主动执行依赖安装。以下 `<连接器目录>` 应替换为实际完整路径；安装可能访问锁文件中的公开依赖源，插件加载本身不会执行安装。

```powershell
uv sync --frozen --no-dev --project '<连接器目录>'
```

已具备本机 stdio 配置能力的客户端，可添加名为 `flipbelt-ai-assets` 的连接器：命令为 `powershell.exe`，参数依次为 `-NoProfile`、`-File`、启动器 `run.ps1` 的绝对路径；千问应另设环境变量 `FLIPBELT_CLIENT_NAME=QwenWork`。启动器只启动已安装依赖，不下载依赖，不更改全局配置。保存后以实际工具发现结果为准。已有同名本机连接器时复用，不重复注册同一服务。

千问办公支持的运行端、企业策略和参数格式需要在目标企业环境确认。本包不含自动加载 `.mcp.json`；企业云端或 Linux 环境不能直接运行该 Windows 适配器，需真实的远程 MCP/逐人授权适配后再启用正式模式。

## 首次连接与登记

1. 先读取 `get_capabilities`。未连接时调用 `start_connection`，向本人展示 verification_uri 与授权码，由本人在网页完成登录与批准。
2. 至少五秒后查询 `complete_connection`；pending 仍是待授权。不要向聊天索取或读取凭据文件。
3. 重新读取能力与本人身份，核对实际16工具及支持字段。工具目录与能力声明均支持时才使用补充资料、人员搜索和附件；不臆造工具。
4. 正式保存前取得用户对保存范围的指示，创建私有草稿或结构化孵化摘要；每次写入保留 request_id。超时先用原编号查 operation_status。
5. 本人打开 confirmation_url 核对确切版本并选择共享范围。Agent不能代点确认。重读状态后区分草稿、已登记待审核与业务验收。

工具集：start_connection、complete_connection、get_capabilities、search_assets、get_asset、create_asset_draft、update_asset_draft、get_my_incubations、get_incubation、save_snapshot、operation_status、disconnect、get_asset_details、save_asset_details、search_people、upload_asset_attachment。实际安装版本可能不同，不能仅凭此列表假称可用。

## 千问办公企业后台

管理员在 AI 管理 → AI 资产管理 → 专家套件上传 ZIP，核对标识、版本、两项技能和目标端，再设置成员开放范围。连接器与套件的市场、成员范围和业务授权分别管理。企业连接器是否允许本机命令型 stdio，须在实际部署验证；不要误选 OAuth 2.1 DCR 并填入当前普通 REST URL。

官方依据：[企业专家套件](https://help.aliyun.com/zh/qwenwork/enterprise-ultimate-ai-assets-expert-kits)、[企业连接器](https://help.aliyun.com/zh/qwenwork/enterprise-ultimate-ai-assets-connectors)。提供的兼容案例记录千问办公 v1.2.5 接受 `.qoder-plugin/plugin.json`，本包采用该形式；它不是本插件在目标企业环境已验收的证据。
