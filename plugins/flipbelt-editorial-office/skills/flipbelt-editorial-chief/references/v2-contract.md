# 共享 V2 语义
唯一机器契约：知识仓 schemas/v2/knowledge-content.schema.json；release 契约为 knowledge-release.schema.json。这里不维护 Schema 副本。
## 对象
Page 类型为 product、size_guide、extended、brand_base、column；稳定 Entity 承载 canonical/aliases/relations，Asset 承载素材身份与校验信息。
page_id、primary_entity_id、section_id、reference_id、asset_id 保持稳定。标题/路径变化不自动创建新实体。content_version 是内容版本，需随实际内容变更按既有版本策略处理，不能视作永远不变的 ID。
对象创建前由关系台检查 Candidate Entity List，不能先造对象再去重。
## 状态
publish_status: draft | ready 表示发布资格；Page/Section 的 knowledge_status: published | pending_test | pending_content | deprecated 表示知识状态；Asset 独立使用 pending | ready | deprecated。
published 不证明已上线。候选、研究、审校与 Job 状态不写入正式对象。状态字段只放 Schema 允许的对象，Reference 不凭空增加状态字段。
pending_test 用于真正缺少面料性能测试的局部知识；非测试内容缺口用 pending_content。不得因仍在补测试把已确认事实整体降级。
正文不写旧方括号缺口标签。Pending Section 沿用所附正文 heading，由阅读端就地表达，不新增“暂无内容”汇总或维护语言。
## 来源、可见性、素材
来源使用 source_id、source_type、authority、citation_title、verified_at 与允许的 public_url；验证日期必须真实。产品来源优先级和外部研究要求由相应编辑定义。
当前默认 internal；partner 必须有实际 allowed_organizations，不发明机构数据。
正式素材通过稳定 Asset ID 绑定 Section，保留 alt_text。缺稳定素材时 assets: []，不伪造资源、不强制把已有正文设为 pending；真实素材缺口登记内部 Tracking。
## 关系
Reference 绑定来源 Section 和 target_entity_id，kind、interaction、occurrence 按 Schema。可交互引用必须有可打开目标 Page；relation 的 target_entity_id 指 Entity，不是 Page ID。
只扩展用户授权的对象，不为编辑部元数据放宽 additionalProperties。
