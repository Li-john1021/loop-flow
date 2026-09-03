# Review 与 Test

本文件在实施单元完成后加载。

## Tier 1

Tier 1 默认执行：

```text
一个实施 Agent
  -> acceptance 最小验收
  -> 独立 Spec Reviewer
  -> 主 Agent 汇总
```

不默认执行 Code Review、独立 Test Agent 或 canonical Trace。无独立 Reviewer 时只能标记 `main_degraded` 或 `not_available`，不能写成独立通过。

## 完整模式

按代码影响串行执行，不并行：

```text
critical/material 代码：Code Review -> 通过后 Spec Review
limited 代码：记录理由，可跳过 Code Review -> Spec Review
none：Code Review not_applicable -> Spec Review
```

Code Review 失败或阻断时立即短路，先建立返工单元或暂停，不启动 Spec Review。每个 Review 使用不同身份和上下文；Review 报告必须记录 `review_executor`。

## Test

Review 通过后，按 Plan 的 `test_mode` 执行独立 Test Agent、人工测试或明确的 `not_available`。测试 Agent 不得是实施 Agent；至少覆盖一条成功路径和适用的失败/拒绝路径。测试通过不等于用户批准，也不替代最终 Spec 对账。

失败只产生 `revise` 或 `blocked`，不能改写成 `done`。详细合同见 `schemas/review-report.schema.json`、`schemas/test-report.schema.json` 和对应模板。
