# Gemini CLI 宿主适配

Gemini CLI 支持从用户级或工作区级 Skill 目录发现 Skill，也支持使用 `/skills list`、`/skills reload` 管理发现结果。命令封装仍以 `commands/manifest.json` 为唯一语义来源。

推荐方式：

```text
gemini skills link <loop-flow-root> --scope workspace
/skills reload
```

之后使用自然语言或宿主支持的 Skill 参数调用 `plan`、`annotate`、`ready`、`approve`、`run`、`status`、`validate`、`resume`、`retro`、`cancel`。若宿主提供斜杠参数，可映射为 `/loop-flow <command> [args]`；不提供时不能伪造原生命令，只需把命令语义转发给 `SKILL.md`。
