# loop-flow retro

仅在周期结束且用户显式调用后使用。主对话在周期结束时只提醒“是否执行 retro”，不得自动运行 Consumer 或消耗高级模型。触发后，派出独立的 `commands/prompts/retro-consumer.md` Session（建议 `frontier` 或用户指定的高级模型）读取脱敏 Trace、Evidence 和 Work Log，再生成优化候选。没有独立上下文时只能标记 `main_degraded/not_available`；消费者无法确认根因时只报告 `insufficient_evidence`。候选必须经过 held-out、对抗测试、质量/成本门禁和用户批准。保留旧版本，是否采纳由用户决定。

参数：`{{ARGS}}`
