# loop-flow

这是一个面向高级个人开发者的轻量主对话编排 Skill。它把长程 Agent 工作的核心方法固化为：

安装和首次检查见 [INSTALL.md](INSTALL.md)。

```text
简单任务：Tier 1 三字段卡 -> Grill 批注 -> 用户确认 -> 最小验收 -> Spec Review
复杂任务：Plan 初稿 -> Grill 批注 -> 用户确认 -> 实施批准
          -> Cycle Spec -> 动态编排 -> Code Review（重要代码时）-> Spec Review
     -> 构建/编译（适用时）-> 独立 Test Agent
     -> Spec 对账 -> Trace / Work Log -> 可选回溯
```

它不是一个独立的模型运行时，也不要求初始化项目、预生成工程师或让用户手工管理多个 Session。主对话负责全局编排；子 Agent 负责有界实施、测试和独立审查。

## 目录

- `SKILL.md`：唯一 Skill 主入口。
- `INSTALL.md`：跨平台安装、更新和 smoke check。
- `schemas/`：Tier 1 Plan、完整 Plan、Cycle Spec、Task、回传、Review、Test、Trace 和 Work Log 的机器可读合同。
- `templates/`：主对话和子 Agent 使用的人类可读模板。
- `examples/`：可直接校验的 Tier 1、完整 Plan、Cycle Spec 和批注实例。
- `references/`：只在任务晋升后加载的完整治理原则。
- `references/decision-record.md`：用户确认的 Review 分级和 Tier 1 策略。
- `references/plan-dialogue.md`：Grill 提问、批注整理和 Plan 批准循环。
- `references/spec-compiler.md`：完整 Plan 到 Cycle Spec 的编译规则。
- `references/orchestration.md`：环境嗅探、模型分层和动态分派。
- `references/review-and-test.md`：Tier 1/完整模式 Review 与测试顺序。
- `references/trace-and-retro.md`：Trace、Work Log、回溯和 SkillOpt。
- `references/storage-layout.md`：`.loop-flow/` 运行产物目录和命名约定。
- `references/command-surface.md`：平台无关命令语义、门控和无感串联规则。
- `adapters/`：Codex、Claude Code 和通用宿主接入说明。
- `agents/openai.yaml`：Codex 的显示元数据。
- `scripts/validate.py`：可选、离线、标准库优先的 Schema/语义自检入口，不是运行时硬依赖。

## Codex 接入

将整个 `loop-flow` 目录放到项目级 `.codex/skills/` 或用户级 Codex skills 目录。加载后可以自然语言触发，例如：

```text
用 loop-flow 为这个目标生成 Plan：<目标>
把所有实施前缺口用 Grill 问题列入 Plan 的 annotations 区
读取我的批注，整理 Plan，并告诉我是否还存在阻断缺口
缺口清零后，询问我是否批准实施
审阅当前 Plan 的批注并整理为下一个版本
批准后编译 Cycle Spec 并开始加工
运行本轮按代码影响串行 Review
让独立 Test Agent 执行测试并回传报告
对本轮进行回溯，提出 Skill 优化候选
```

如果 Codex 当前环境不提供 subagent，Skill 必须退化为串行，并在 Work Log 中记录能力缺失。

## 可选命令入口

命令只是快捷入口，不会替代主对话的讨论、Plan 批注和用户批准。常用语义为：

```text
plan -> annotate -> ready -> approve -> run
status / validate / resume / retro / cancel
```

`run` 批准后自动串联适用的编译、分派、Review、构建、测试、对账和 Trace；用户不必逐阶段调用命令。

## Claude Code 接入

将整个目录放到项目级 `.claude/skills/` 或用户级 Claude Code skills 目录。Claude Code 可以通过 Skill 选择器或自然语言加载同一份 `SKILL.md`。不要依赖特定 Hook；Hook 只能加速 Trace 或停止检查，不能替代 Schema、独立 Review 或用户批准。

可选离线自检：

```text
python skills/loop-flow/scripts/validate.py --root skills/loop-flow
```

计算批准指纹时使用唯一入口：

```text
python skills/loop-flow/scripts/validate.py --fingerprint-plan path/to/plan.json
```

该脚本不是 Skill 的硬依赖；缺少 `jsonschema` 时会明确输出结构化降级状态。

## 使用边界

- Schema 为 `1.0` 合同；批注使用 `schemas/plan-annotation.schema.json`，宿主可以使用标准 JSON Schema 校验器，也可以使用等价语义校验实现。
- `schemas/` 和 `templates/` 是本 Skill 的资源，不是额外的子 Skill。
- 不要把私有演进叙事、原始 prompt、完整 transcript 或雇主材料放进 Skill 运行上下文。
- 不要把测试案例的 Human Proxy Session 当成生产用户必须操作的界面。
- 外部 API、凭据、付费模型、发布和破坏性命令必须单独取得用户授权。

版本：`0.1.0-alpha.1`
语言：中文说明；命令、Schema 字段和宿主标识保留英文。
