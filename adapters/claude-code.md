# Claude Code 宿主适配

## 最小能力

Claude Code 读取同一份 `SKILL.md`，用原生 Agent/Skill 能力承载主对话与子 Agent。项目级或用户级 Skill 目录均可安装本包。

## Hook 边界

Hook 只能用于提醒、Trace、停止检查或生成报告。不能假设 Hook 必然存在，也不能用 Hook 替代 Schema、独立 Review、Test Agent 或用户批准。没有可强制 Hook 时必须报告 `hook_unavailable`，流程仍可通过文档和结构化合同继续。

## 分派规则

- 由主对话为每个子 Agent 提供 Task Envelope 和最小上下文。
- Code Review（如代码影响为 critical/material）与 Spec Review 按顺序使用不同子 Agent 或不同干净上下文；Code Review 未通过时不启动 Spec Review。
- Review 报告必须记录 `review_executor`；无独立子 Agent 时使用 `manual_reviewer/main_degraded`，不得填写 `independent_subagent`。
- Test Agent 不得是实施 Agent 的同一身份。
- 原始 transcript、私有推理和无关历史不回灌主对话。

## 命令映射

Claude Code 将 Skill 名称作为命令入口；推荐直接使用：

```text
/loop-flow plan
/loop-flow annotate
/loop-flow ready
/loop-flow approve
/loop-flow spec
/loop-flow run all
/loop-flow status
/loop-flow validate
/loop-flow resume
/loop-flow retro
/loop-flow cancel
```

参数由同一个 `loop-flow` Skill 接收，再按 `commands/manifest.json` 转发到共用提示词。命令只是快捷入口；自然语言仍可无感触发同一流程。若宿主未发现新 Skill，按平台规则刷新或重启会话。
