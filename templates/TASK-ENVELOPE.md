# Task Envelope：<WU-ID>

```yaml
schema_version: "1.0"
envelope_id: envelope:<id>
spec_ref: spec:<id>
unit_ref: WU-001
role_type: implementer
model_tier: economy
context_refs:
  - <只列当前单元必要材料>
acceptance_refs:
  - AC-001
allowed_paths:
  - <允许读写路径>
forbidden_effects:
  - <不得发生的效果>
budget:
  # 未设置上限时删除对应字段；不要使用 0
  max_attempts: 1
stop_conditions:
  - artifact_ready
  - clarification_needed
  - blocked
output_contract: unit_result
```

只执行当前单元，不扩大范围。不要把完整仓库、演进叙事、私有日志或无关历史装入上下文。完成后必须返回 Unit Result，不要只发送自然语言总结。
