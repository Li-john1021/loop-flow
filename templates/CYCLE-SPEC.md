# Cycle Spec：<本轮目标>

```yaml
schema_version: "1.0"
spec_id: spec:<slug>:<cycle>
plan_ref: plan:<slug>
plan_version: 1
plan_fingerprint: sha256:<64 hex>
```

## Requirements 与 Acceptance

只复制已批准 Plan 的原子要求，并为每项要求绑定至少一个可执行 Acceptance。不得在本文件加入 Plan 没有决定的行为。

## Work Units

| ID | 目标 | 依赖 | Requirement | Acceptance | 检查 | 允许路径 | 禁止效果 | 模型层级 | 代码影响 | Code Review | Review 顺序 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| WU-001 |  |  |  |  |  |  |  | economy | `limited`/`none` | `optional`/`not_applicable` | `code_review_then_spec_review`/`spec_review_only` |

## Invariants

-

## Forbidden Effects

-

## Validation Policy

- Review：`sequential_conditional`
- Review 执行者：`independent_subagent / manual_reviewer / main_degraded`
- 每个 Work Unit 必须填写代码影响、Code Review 策略、理由和 Review 顺序。
- 约束：`critical/material` 不得跳过 Code Review；`limited` 可选但必须有理由；`none` 必须为 `not_applicable` 并使用 `spec_review_only`。
- Build：`when_applicable`
- Test：`independent_subagent`
- 必须由独立上下文执行，不接受实施自述。

## Final Acceptance

- 所有 Requirement 都有实际 Evidence。
- 所需的 Review 按 `review_sequence` 顺序通过，且没有未处理的高/中 Finding。
- 适用的构建和独立测试与当前候选一致。
- 用户批准的不可逆范围没有越界。
- 结束状态只能是 `done / revise / planning_review / blocked / not_available`。
