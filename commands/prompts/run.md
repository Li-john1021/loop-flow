# loop-flow run

加载根目录 `SKILL.md` 和当前阶段所需 reference。确认入口条件后再启动无感串联：完整模式必须已有与批准 Plan 指纹和版本一致的冻结 Cycle Spec，然后按适用性执行动态分派、Code Review、Spec Review、构建、独立测试、对账和 Trace；Tier 1 只需已批准任务卡并执行最小闭环。

没有冻结 Spec、Spec 已过期或指纹不一致时，拒绝执行并提示先运行 `spec`；不得在 `run` 内静默编译。

`--step` 只允许调试或恢复已授权步骤，不能跳过批准、Review、测试、路径和安全门。失败或证据不足必须保留 `revise/blocked/not_available`。

参数：`{{ARGS}}`
