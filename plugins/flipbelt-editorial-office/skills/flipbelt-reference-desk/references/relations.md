# 关系规则
一个概念一个主 Entity；注册符号、缩写、译名、历史名可作为 Alias，但先核对是否真同义。品牌≠技术，指标≠方法，标准≠版本。
Candidate Entity List 在创建前形成，记录候选、现有匹配、规范名、实体类型、目标 Page、证据和决定。
negative_aliases 不合并；parent/child 不自指、不形成直接循环。实体边的 target_entity_id 必须为 Entity ID。related 不用来掩盖未知关系。
同页首次出现按 Schema 建 Reference；kind 为 definition/related/comparison/evidence，interaction 按允许枚举，occurrence 为 first。可交互链接需有目标 Entity 及可打开 Page。
产品通用概念可转到已存在扩展目标，但产品专属事实保留。Extended 的 applies_to 连接实际使用产品的 Entity；产品事实不得由这种边推导。
## 报告分类
EXISTING 已有可用目标；ALIAS 同义词指已确认 canonical；MISSING 找不到可用目标；CANDIDATE 待研究候选；BROKEN 已有引用失效；DUPLICATE 疑似重复待裁决；DEPRECATED 目标已废弃需判断替代。
这些分类不是 Schema 状态。缺目标只登记现有 Tracking 的 wiki_candidate，用户未授权扩展写作不创建正文。确认重复不自动授权删除实体或跨页批量替换。
## 既定范围约束
终审词表允许套结、四针六线、平锁缝、绷缝、包缝、锁式线迹；不创建以“缝纫线迹”开头的总主题，不重新引入 GB/T 4515、GB/T 24118、ISO 4915 独立发布 Entity。旧“极致人体工学与结构车缝”不再是保护对象，但不因此自动删除。
词库中的 protected/published/candidate 只描述历史索引，不覆盖当前 V2 或用户当前决定。
## 失败
ID 不存在、Alias 冲突、目标不可打开属于具体错误；报告精确来源对象/Section、目标 ID、候选替代及证据。存在 source/target 状态或权限差异时检查实际可见性，不以“ID 存在”当可用。
