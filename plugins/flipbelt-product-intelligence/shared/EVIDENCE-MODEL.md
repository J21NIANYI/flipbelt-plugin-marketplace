# Evidence Model

每项关键结论使用以下字段：

```yaml
claim: "结论摘要"
source_class: "A|B|C|D|E"
temporal_class: "stable|dynamic"
status: "verified|inferred|unknown"
source_ref: "release/page/asset identifier or URL"
checked_at: "ISO 8601 timestamp or current session"
valid_for: "release identity or bounded forecast/event window"
```

- A：FlipBelt 发布事实。
- B：权威外部证据。
- C：专业参考。
- D：明确专家推论，必须指向 A/B/C 依据。
- E：未知。

`dynamic` 只是时间属性，不改变来源等级。当前天气、赛事状态和官方临时公告不得被描述为永久事实。
