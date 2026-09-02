# 跨文件语义检查

本清单只在 Tier 1 触发晋升、用户明确要求完整治理，或完整周期结束时加载。Tier 1 未晋升时只检查任务卡、实际验收观察、Spec Review 结果和用户决定。

## 编译时检查

1. `Plan.status=approved` 与 `approval.status=approved` 必须同时成立；任一批准指纹必须由唯一命令计算。
2. 每个 `AC-*` 必须引用当前 Plan 中存在的 `REQ-*`。
3. Cycle Spec 中的每个 `REQ-*` 必须通过 `source_refs` 直接引用当前批准 Plan 的 `REQ-*`，或使用 `plan:<id>#REQ-xxx` 形式追溯；允许拆分为新 ID，但不得存在无 Plan 来源的孤立 ID。`AC-*` 必须引用当前 Spec 的 `REQ-*`。
4. 每个 `WU-*` 的 `requirement_refs`、`acceptance_refs` 必须引用当前 Spec 中存在的 ID。
5. 每个 `depends_on` 必须引用存在的 `WU-*`，依赖图不得成环。
6. 当前 Cycle Spec 中的所有 Requirement 至少被一个 Work Unit 覆盖；若未来要区分 `should/could`，必须在 Cycle Spec 增加 priority 字段后再放宽此规则。
7. Spec 的 `plan_ref`、`plan_version`、`plan_fingerprint` 必须匹配批准 Plan。
8. `critical/material` 必须为 `code_review_policy=required` 且顺序为 `code_review_then_spec_review`。
9. `limited` 只能为 `required/optional`；`not_applicable` 只允许 `none`。
10. 没有独立子 Agent 时，`review_executor` 必须为 `manual_reviewer` 或 `main_degraded`；不得声称 independent。执行者绑定以 Trace 的 `unit_dispatched` 事件为准，不另设权威 Ledger。

## 周期结束检查

1. 每项 Acceptance 都有实际 Artifact、Evidence、Review 或 Test 引用。
2. Review/Test actor 不得等于实施 actor；context ref 不得与实施上下文相同。
3. Code Review（如 required）必须先有 `pass`，之后才允许 Spec Review；顺序由 Trace 的 `review_completed` 事件核对。
4. 完整 Work Log 的每个条目必须至少引用一个真实 Trace event ID。
5. 报告与 Artifact 的 candidate fingerprint 必须对应当前候选。
6. `manual/main_degraded/not_available` 不得描述为完整独立验证通过。
7. Tier 1 `rework_count` 达到 2 时，必须晋升完整模式并冻结 Spec/指纹。

失败路由：需要用户决定则 `planning_review`；当前范围内可修复则 `revise`；外部能力阻断则 `blocked`；可选能力未启用则 `not_available`。
