# loop-flow

> **写好 Plan，雷霆回车，然后去干别的。剩下的，你的 Agent 大人会用 Spec、按风险 Review、独立测试和 Trace 一路看守到交付。**

loop-flow 不是框架，不是运行时，是一个拷进 skills 目录就能用的编排 Skill——从我平时和 Agent 协同开发的流程里提炼，用 SDD（规范驱动开发）的逻辑组织，加上了 loop-engineering 式的异步校验。

## 它解决什么

**模型觉得自己实现了，但其实没实现**——这是 vibe coding 最经典的幻觉。loop-flow 的解法不是“更认真地叮嘱模型”，而是让证据说话：

- **先合同后代码**：Plan → 固定格式批注收敛需求 → 用户批准 → 冻结 Cycle Spec，然后才允许动手；
- **异步校验**：实施、Code Review、Spec Review、独立测试由不同上下文的 Agent 串行把关，退出码、文件指纹和实际 Artifact 算数，聊天里的“完成了”不算数；
- **越用越顺手**：每个周期留下最小 Trace；你显式触发回溯时，独立消费者分析失败根因（提示词 / 任务拆分 / 流程 / 模型 / 环境），产出优化候选，经你批准后进化工作流。理论上几轮之后，它会越来越贴合你的个人开发习惯。

## 适合谁

- 🍼 **刚开始 vibe coding、不太懂软件怎么开发的文科宝宝**——批注门会逼着把“要什么”在写代码之前说清楚；
- 🧵 **想多线程开发的人**——小任务三字段卡片秒级启动，复杂任务按触发器自动升级完整流程；
- 😴 **和我一样写完 Plan 一个回车就回去睡大觉的懒人**——批准后 `run` 自动串起编译、实施、审查、测试和对账，醒来收货。

## 使用前必读

- 💸 **心疼 token 之人慎用**。省钱姿势是内建的：高级模型写 Plan，经济模型实施（模型分层是一等公民）。
- 🔌 **clone 回去之后，记得让你的 Agent 大人做自己的平台适配**（Claude Code / Codex / Gemini CLI 的安装方式见 [INSTALL.md](INSTALL.md)）。

安装和首次检查见 [INSTALL.md](INSTALL.md)。

## 目录

- `SKILL.md`：唯一 Skill 主入口。
- `INSTALL.md`：跨平台安装、更新和 smoke check。
- `schemas/`：Tier 1 Plan、完整 Plan、Cycle Spec、Task、回传、Review、Test、Trace、Work Log 和优化候选的机器可读合同。
- `templates/`：主对话和子 Agent 使用的人类可读模板。
- `examples/`：可直接校验的 Tier 1、完整 Plan、Cycle Spec 和批注实例。
- `commands/`：平台无关命令清单和薄转发提示词，不是第二套状态机。
- `.github/workflows/ci.yml`：公开仓库的 Schema、语义、命令清单和单元测试门禁。
- `references/`：只在任务晋升后加载的完整治理原则。
- `references/decision-record.md`：用户确认的 Review 分级和 Tier 1 策略。
- `references/plan-dialogue.md`：Grill 提问、批注整理和 Plan 批准循环。
- `references/spec-compiler.md`：完整 Plan 到 Cycle Spec 的编译规则。
- `references/orchestration.md`：环境嗅探、模型分层和动态分派。
- `references/review-and-test.md`：Tier 1/完整模式 Review 与测试顺序。
- `references/trace-and-retro.md`：Trace、Work Log、回溯和 SkillOpt。
- `references/evolution.md`：根因分类、能力不匹配门和优化候选生命周期。
- `references/storage-layout.md`：`.loop-flow/` 运行产物目录和命名约定。
- `references/command-surface.md`：平台无关命令语义、门控和无感串联规则。
- `adapters/`：Codex、Claude Code 和通用宿主接入说明。
- `adapters/gemini-cli.md`：Gemini CLI 的 Skill 发现和命令映射说明。
- `agents/openai.yaml`：Codex 的显示元数据。
- `scripts/validate.py`：可选、离线、标准库优先的 Schema/语义自检入口，不是运行时硬依赖。
- `scripts/consume_trace.py`：可选、离线 Trace Consumer，只生成优化候选，不自动修改 Skill。

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
plan -> annotate -> ready -> approve -> spec -> run
status / validate / resume / retro / cancel
```

完整模式的命令顺序是 `plan -> annotate -> ready -> approve -> spec -> run`；Tier 1 在批准任务卡后可直接 `run`。命令清单和薄转发提示词见 `commands/manifest.json` 与 `commands/prompts/`。宿主可以把它们映射为原生命令；不支持命令的宿主继续使用自然语言，不影响无感串联。

`run` 在 Tier 1 已批准任务卡或完整模式已冻结 Spec 后自动串联适用的分派、Review、构建、测试、对账和 Trace；用户不必逐阶段调用内部命令。

仓库自检也可直接运行：

```text
python -m pip install jsonschema
python -B scripts/validate.py --root . --require-jsonschema
python -B -m unittest discover -s tests -v
```

完成周期后不会自动消费 Trace。用户显式触发 `retro` 后，才由独立高级上下文消费 Trace：

```text
python -B scripts/consume_trace.py --trace-dir <project>/.loop-flow/trace --root . --require-jsonschema --output <project>/.loop-flow/decisions/optimization-report.json
```

Consumer 只生成 `optimization-candidate`，不会自动修改提示词、Plan 或 Skill；候选必须经过独立评估和用户批准。

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

版本：`0.1.0-alpha.3`
语言：中文说明；命令、Schema 字段和宿主标识保留英文。
