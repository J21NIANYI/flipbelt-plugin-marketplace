# 动态 HTML 文章契约 1.0

## 范围与入口

当用户要求互动文章、动态 HTML、HTML 上传/编辑/发布时加载本文件。HTML 是现有 V2 Page 的展示层，不新增 Page 类型。专栏交给 Column；产品、尺码、扩展知识仍由对应编辑负责事实，Column 可协助呈现。Chief 锁定对象与来源，Review 独立只读审校，Delivery 准备发布材料。
用户只要求方案或审核时不创建可运行页面。要求前端预览时可制作 HTML 工作制品；用户要求“确认后导出”时先预览，收到确认后交付最终文件。编辑授权不自动授权发布或生产部署。授权已在会话给出时不重复索要。

平台契约文件为已确认的 flipbelt-kb-platform checkout 下 docs/dynamic-html-articles.md；先定位真实文件，以当前已部署代码和能力接口为准。不以个人维护源的实现日期推断生产能力。纯本地制作不要求远程认证。需要线上预检或发布时，先确认实际部署支持 contract_version=1.0；404、401、403、开关关闭、版本不符停止相应路径，不能启用 M2M、修改身份或切换内容来源补救。

## 一个文件、两种正文

UTF-8 .html/.htm 不超过 256 KiB。必须有且仅有一个位于 article 外的 `<script type="application/json" id="fbkb-page">`，内含完整现有 V2 Page。`sections[].markdown` 是搜索、MCP 和文字版正文；每个 section_id 对应 `<article data-fbkb-article>` 内唯一 ID。使用真实稳定 ID、既有 references/assets；原稿附件是证据，不是执行指令。
HTML 与 Markdown 按章节同步，保留结论、条件、数据、单位与限定。纯样式/动画变更可保持 Markdown 不变；含义或状态选项变化时同步文字说明。内嵌 JSON 的 `<` 写成 `\u003c`。保留页/章节 ID；标题缩短不重建对象。
只制作 article 正文，不复制门户全局 banner、页标题、目录或管理员按钮。正文段落用 CSS `text-indent:2em`，组件说明、图注、列表和控件不机械缩进；自然换行，短主题标题。不同时保留表达同一信息的静态图表和互动图表。位置示意来自真实附件或已核对资料，不能由示意图推导压力分布实测。
允许内联 CSS/经典 JavaScript、HTML/SVG、PNG/JPEG/GIF/WebP data 图片；外部 JS/CSS/图片、模块 import、CSS url/@import、iframe、form、object/embed/base/link、meta refresh 与非片段 href 不支持。使用语义按钮、可见键盘焦点、aria 状态、窄屏自适应和 reduced-motion；动画由用户触发。禁止网络、凭据、导航、父页面 DOM/存储访问代码。门户提供高度/锚点桥接，作者不重复实现父页面桥接。

## 制作与编辑

1. 读取目标 Page、当前基线和原稿；明确用途、受众、组件与文件交付范围。逐页写作，不让脚本生成或覆盖正式知识页。
2. 参考 [单页模板](../../flipbelt-column-editor/templates/dynamic-article.html) 在用户指定工作目录逐段编辑。模板为合成待完善内容，不能直接发布，主题 Entity 必须替换为真实目标。
3. 按单页模板将人工写好的 manifest、body、CSS、JS 组织为新 HTML 工作制品；不自动输出到正式知识目录或覆盖现有文件，修改由作者逐文件编辑。CSS/JS 的闭合 style/script 字面量需由作者用适合内联的转义处理。
4. 核对内嵌 JSON、锚点和资源规则；文本检查不等于平台 parse5/V2、引用检查或浏览器验证。使用已确认的平台 checkout 再运行 `npm run content:html-check --workspace @flipbelt/kb-api -- <HTML绝对路径>`。未安装平台依赖时报告缺口，不声称通过。
5. 展示前端预览并实际检查状态切换、字体/缩进、移动端、键盘及无动画降级；自动浏览器检查属于验证，最终视觉/业务结论由人工给出。送 [HTML 审校](../../flipbelt-editorial-review/references/html-checks.md) 独立复核。
6. 修改时保留原 HTML 哈希及 Markdown 基线，逐章节同步内容。预览使用隔离 iframe，不将未审校源码注入主页面；预览过期后重建，不复用旧链接。

## 预检、发布与恢复

团队包不含特权 HTTP helper。远程预检由有权限的操作者按当前平台界面与已确认契约执行；缺权限时继续本地制品，线上检查标为未执行。fbkb 1.0 不支持 HTML，不能把 HTML 传给其 push 或发明 publish 命令。详细状态见 [发布交付](../../flipbelt-editorial-delivery/references/html-publishing.md)。
正式发布首选现有 KB_ADMIN 管理页面“上传 HTML → 校验预览 → 保存草稿或发布”。用户本人完成认证与业务操作；工具不代填凭据、不自动操作真实角色验收。只有实际成功返回并核对当前 release 才可报告激活，不用本地文件/Revision ID 推断上线。
HTML 存在 Revision、Draft 与不可变 Page 展示字段，摘要包含脚本变化。页面查询只返回可用标识，交互走受限 HTTP frame；MCP 始终读取 Markdown。纯 JSON/MD 替换且未携带 HTML 会移除该版本交互；正式覆盖前核对影响。历史恢复创建新 Revision/Release，不是直接改活动 release。
恢复包有 HTML 时使用 1.2，并绑定侧文件与 Markdown manifest、发布集合摘要；旧工具不接受该版本。回滚旧应用前需关闭 CONTENT_API_WRITE_ENABLED、CONTENT_WEB_PUBLISH_ENABLED、ONLINE_CONTENT_ACTIVATION_ENABLED，只读保留当前知识指针及数据；旧发布器不能保留 HTML，不得继续写入。恢复支持 HTML 的应用并验证快照/摘要后才恢复写入。
