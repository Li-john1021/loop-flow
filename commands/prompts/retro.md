# loop-flow retro

仅在周期结束后使用。先运行 `python scripts/consume_trace.py --trace-dir <project>/.loop-flow/trace --root <loop-flow-root> --require-jsonschema --output <project>/.loop-flow/decisions/optimization-report.json`，再把报告交给独立 Consumer/Judge Session 基于实际 Trace、Evidence 和 Work Log 提出上下文压缩、模型分层、任务拆分、Review 或提示词优化候选。没有独立上下文时只能标记 `main_degraded/not_available`；消费者无法确认根因时只报告 `insufficient_evidence`。候选必须经过 held-out、对抗测试、质量/成本门禁和用户批准。保留旧版本，是否采纳由用户决定。

参数：`{{ARGS}}`
