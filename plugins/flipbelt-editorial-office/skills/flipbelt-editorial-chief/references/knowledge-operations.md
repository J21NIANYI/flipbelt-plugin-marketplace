# fbkb 本地操作与团队交付

## 可用路径
FlipBelt Knowledge App 的读取工具不写 Revision 或激活 Release。云端先交付基于当前页面与原稿的逐页修改单、差异、草稿和审校材料；不虚构本机命令结果。
已授权本地编辑且真实工作区与现有 fbkb 可访问时，先定位实际安装入口，运行 doctor --json，核对退出码 0、contract_version=1.0。缺入口、依赖或版本不符时标记相关步骤 BLOCKED，不猜路径、不自行安装认证工具。

## 本地检查
逐页编辑前在受控知识根之外保留真实基线与哈希，不覆盖已有基线。新建对象用显式空 JSON 对象作比较基线并标记 create。
逐页执行 validate <候选路径> --json、preview <候选路径> --json、diff <基线路径> <候选路径> --json；缺基线只阻断 diff，不用候选自身冒充基线。JSON Page 在完整 V2 上下文中校验；Entity/Asset 使用全库 validate --json，不交给 Page Publisher。
工具只做盘点、预览和确定性校验，不生成或批量重写正式正文。JSON 本地检查不要求生产连接；Markdown/远程检查若需要现有授权环境，先核对实际工具契约与任务范围，缺认证交付本地材料并标记未执行，不获取或代填凭据。

## Revision 与发布
本包不分发远程 HTTP helper、Token 或认证配置。只有目标、范围和 Revision 提交动作获得明确授权，且宿主已有真实可用的受控提交工具时，才按该工具当前契约先 dry-run、再提交。409 停止逐页对账；结果不明保留同一候选与基线，先核对，不强制覆盖。
只读 App 不能执行提交。无受控工具时由有权限的操作者使用现有管理员入口处理草稿和发布；不得拼接 App HTTP 接口、启用 M2M 或扩大权限补救。
仅有真实 revision_submitted 回执时报告 Revision 已提交，并附实际 document_id、revision_id、version、content_sha256；缺字段写未返回。dry-run 通过不等于提交，Revision 不等于活动 Release。

## 审校与 HTML
独立审校读取真实基线、来源、差异及实际工具结果，工具成功不等于语义审校或人工验收。动态 HTML 按 [动态契约](dynamic-html.md) 和 [管理员交付](../../flipbelt-editorial-delivery/references/html-publishing.md) 处理；fbkb 1.0 不支持 HTML，不把 HTML 传入 push。
分开报告本地变更、自动检查、Revision 提交、Release 激活和人工验收；未执行项不能写 PASS。
