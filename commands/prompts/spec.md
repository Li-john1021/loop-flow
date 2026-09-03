# loop-flow spec

加载根目录 `SKILL.md`、`references/spec-compiler.md` 和当前完整 Plan。仅当完整 Plan 已由用户批准、必填批注已关闭且 Plan 未过期时，编译并冻结本轮 Cycle Spec：

- 运行 Schema、引用、依赖、覆盖、Review 顺序和指纹检查；
- 将结果写入 `.loop-flow/cycles/`，保留旧版，不覆盖已有 Spec；
- Spec 指纹和 `plan_ref/plan_version` 必须对应批准 Plan；
- 已存在且指纹一致时返回“已冻结，无变化”；Plan 版本变化或指纹不一致时保留旧 Spec 并生成新的冻结版本。

Tier 1 不使用此命令；应直接由批准任务卡进入 `run`。

参数：`{{ARGS}}`
