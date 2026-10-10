# 任务路由
| 意图/对象 | 负责 Skill |
|---|---|
| 产品正文、Header、内部 brand_base、产品资料入库 | [product-editor](../../flipbelt-product-editor/SKILL.md) |
| size_guide、完整规格、推荐表、口袋逐尺码数据 | [size-editor](../../flipbelt-size-editor/SKILL.md) |
| 明确创建/修订/核验扩展知识 | [extended-editor](../../flipbelt-extended-editor/SKILL.md) |
| 专栏原稿整理或专栏写作 | [column-editor](../../flipbelt-column-editor/SKILL.md) |
| 引用检查、canonical、Alias、断链、候选 | [reference-desk](../../flipbelt-reference-desk/SKILL.md) |
| 动态 HTML 制作、修改、预览、发布交付 | 事实按现有类型编辑；呈现由 [column-editor](../../flipbelt-column-editor/SKILL.md) 协助，遵循 [动态契约](dynamic-html.md) |
| 独立审校 | [editorial-review](../../flipbelt-editorial-review/SKILL.md) |
| 修改单、回流材料、交付 | [editorial-delivery](../../flipbelt-editorial-delivery/SKILL.md) |

纯产品问答、培训、详情页审查属于本插件之外的只读下游能力。依据当前宿主已安装能力和仓库规则选择，不假定旧名 flipbelt-local-knowledge-base、flipbelt-online-knowledge-base、flipbelt-doc-review 一定存在；不可用则如实报告，不以编辑器替代查询。
产品+尺码拆对象；扩展+产品关联先扩展目标后产品源引用。品牌内部事实由 product-editor 的品牌模式维护；公开品牌技术百科由 extended-editor 维护。

## 级别
L1：单页单点，无结构与共享依赖变化，默认输出修改单；用户明确要求本地修改时仍执行相应编辑与检查，不以分级拒绝授权。
L2：单页多段或结构修订，逐页本地编辑。
L3：多页同类任务，先列目标再逐页处理。
L4：跨类型内容项目，建立依赖顺序与唯一对象所有者。
级别不代替 T0–T3 风险。参数、来源、共享实体、权限或删除按风险升级检查。
开编辑会授权分析选题，不等于授权创建所有选题。用户明确“创建词条并关联产品”已授权两条路径，无需重复确认。
