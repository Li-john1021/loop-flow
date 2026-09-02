# loop-flow

这是一个面向高级个人开发者的轻量主对话编排 Skill。它把长程 Agent 工作的核心方法固化为：

```text
Plan -> Plan Schema -> 用户批注/整理 -> 用户批准
     -> Cycle Spec -> 主对话动态编排
     -> 简单任务：Tier 1 三字段卡 -> 最小验收 -> Spec Review
     -> 复杂任务：完整 Plan/Cycle Spec -> 有界实施 Agent -> Code Review（重要代码时）-> Spec Review
     -> 构建/编译（适用时）-> 独立 Test Agent
     -> Spec 对账 -> Trace / Work Log -> 可选回溯
```

它不是一个独立的模型运行时，也不要求初始化项目、预生成工程师或让用户手工管理多个 Session。主对话负责全局编排；子 Agent 负责有界实施、测试和独立审查。

## 目录

- `SKILL.md`：唯一 Skill 主入口。
- `schemas/`：Tier 1 Plan、完整 Plan、Cycle Spec、Task、回传、Review、Test、Trace 和 Work Log 的机器可读合同。
- `templates/`：主对话和子 Agent 使用的人类可读模板。
- `examples/`：可直接校验的最小 Plan 实例。
- `references/`：只在任务晋升后加载的完整治理原则。
- `references/decision-record.md`：用户确认的 Review 分级和 Tier 1 策略。
- `adapters/`：Codex、Claude Code 和通用宿主接入说明。
- `agents/openai.yaml`：Codex 的显示元数据。
- `scripts/validate.py`：可选、离线、标准库优先的 Schema/语义自检入口，不是运行时硬依赖。

## Codex 接入

将整个 `loop-flow` 目录放到项目级 `.codex/skills/` 或用户级 Codex skills 目录。加载后可以自然语言触发，例如：

```text
用 loop-flow 为这个目标生成 Plan：<目标>
审阅当前 Plan 的批注并整理为下一个版本
批准后编译 Cycle Spec 并开始加工
运行本轮按代码影响串行 Review
让独立 Test Agent 执行测试并回传报告
对本轮进行回溯，提出 Skill 优化候选
```

如果 Codex 当前环境不提供 subagent，Skill 必须退化为串行，并在 Work Log 中记录能力缺失。

## Claude Code 接入

将整个目录放到项目级 `.claude/skills/` 或用户级 Claude Code skills 目录。Claude Code 可以通过 Skill 选择器或自然语言加载同一份 `SKILL.md`。不要依赖特定 Hook；Hook 只能加速 Trace 或停止检查，不能替代 Schema、独立 Review 或用户批准。

可选离线自检：

```text
python skills/loop-flow/scripts/validate.py --root skills/loop-flow
```

该脚本不是 Skill 的硬依赖；缺少 `jsonschema` 时会明确输出结构化降级状态。

## 使用边界

- Schema 为 `1.0` 合同；宿主可以使用标准 JSON Schema 校验器，也可以使用等价语义校验实现。
- `schemas/` 和 `templates/` 是本 Skill 的资源，不是额外的子 Skill。
- 不要把私有演进叙事、原始 prompt、完整 transcript 或雇主材料放进 Skill 运行上下文。
- 不要把测试案例的 Human Proxy Session 当成生产用户必须操作的界面。
- 外部 API、凭据、付费模型、发布和破坏性命令必须单独取得用户授权。

版本：`0.1.0-alpha.1`
语言：中文说明；命令、Schema 字段和宿主标识保留英文。
