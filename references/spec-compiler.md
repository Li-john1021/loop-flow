# Spec 编译

本文件只在 Tier 1 触发升级或用户明确要求完整治理时加载。

## 输入与输出

- 输入：已批准的完整 Plan、Plan 版本、批准指纹和已确认批注；
- 输出：本轮冻结的 Cycle Spec，使用 `schemas/cycle-spec.schema.json`；
- 状态：Spec 是本轮中间合同，不替代长期 Plan，也不记录运行状态。

## 编译规则

允许把复合 Requirement 拆成原子 Requirement、分配 Work Unit、连接 Acceptance 和归一化执行政策。拆分后的新 ID 必须在 `source_refs` 中追溯到批准 Plan 的原 Requirement。

禁止补写 Plan 没有决定的行为、把假设当事实、删除不可验证目标、扩大用户范围或让 Reviewer 修改冻结 Spec。

编译完成后运行 `references/semantic-checks.md` 的编译检查，以及可选的：

```text
python scripts/validate.py --root <loop-flow-root> --plan <plan.json> --cycle-spec <cycle-spec.json> --require-jsonschema
```

若 Plan/Spec 指纹、Requirement/Acceptance/Work Unit 引用、依赖图、覆盖范围或 Review 顺序不一致，返回 `planning_review` 或 `revise`，不得让实施 Agent 猜测。
