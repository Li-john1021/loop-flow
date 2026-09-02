# Review Report：<review-id>

```yaml
schema_version: "1.0"
review_id: review:<id>
review_kind: code_review
reviewer: reviewer:<id>
review_executor: independent_subagent
reviewer_context_ref: context:review:<id>
implementation_actor_refs:
  - worker:<id>
candidate_ref: <候选引用或指纹>
candidate_fingerprint: sha256:<64 hex>
verdict: pass
evidence: []
findings: []
next_cycle_brief:
  objective: <下一步目标>
  allowed_changes: []
  checks: []
  prohibited: []
```

审查者不能修改实现、Plan、Spec、阈值或治理规则。`revise` 必须指出位置、对应 Requirement、证据、严重性、置信度和修复路由。
`reviewer` 不得等于 `implementation_actor_refs` 中任一身份；`reviewer_context_ref` 必须与实施上下文不同。主编排器必须用当前周期 Trace 中的 `unit_dispatched` 事件复核这些字段，不能只相信审查者自述；这里不另设一套 Ledger。
