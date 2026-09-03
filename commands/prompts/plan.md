# loop-flow plan

加载根目录 `SKILL.md` 和 `references/command-surface.md`。根据当前主对话已经确认的内容生成或更新 Plan：

- 讨论不足时先提出 Grill 问题，不把未确认的假设写成决定；
- Plan 可以带 `annotations` 初稿，但不得实施或批准；
- 更新已有 Plan 时递增 `plan_version`，保留旧版本和批注；
- Tier 1 只保留 `goal`、`acceptance`、`forbidden`，命中触发器再晋升。

参数：`{{ARGS}}`
