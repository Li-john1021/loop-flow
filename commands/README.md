# 命令封装

`manifest.json` 是平台无关的命令清单，`prompts/` 是对应的薄转发提示词。这里不是第二套 Skill，也不实现另一套状态机。

宿主适配器只需完成三件事：

1. 读取命令 ID 和参数；
2. 转发到对应的 `prompts/<id>.md`，并加载根目录 `SKILL.md`；
3. 让主对话继续执行原有 Plan、批注、批准、`spec`、`run` 和 `retro` 门控。

宿主应将实际命令参数替换到提示词中的 `{{ARGS}}`；无参数时传入空字符串。不得把参数拼接为可执行 shell 命令。

命令不存在、参数不明或宿主不支持命令时，退化为自然语言请求；不能因为命令入口缺失而伪造阶段已完成。

## 调用形态

```text
plan [当前讨论上下文]
annotate [用户批注或答案]
ready
approve
spec
run [WU-id|--step|all]
status
validate
resume
retro
cancel
```

完整模式必须先执行 `approve` 再执行 `spec` 冻结 Cycle Spec，之后 `run` 默认执行 `all`。Tier 1 不生成 Spec，批准任务卡后可直接 `run`。`--step` 只用于已授权的调试或恢复步骤，不能跳过门控。
