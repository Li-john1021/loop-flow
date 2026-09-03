---
name: loop-flow
description: 用一个主对话先生成 Plan，再通过固定批注和用户确认逐步收敛；复杂时才升级 Spec、子 Agent、串行 Code/Spec Review、独立测试、Trace 和回溯。适用于代码、文本、研究及其他可验证长任务。
---

# Loop Flow

这是一个主对话编排 Skill，不是独立 Agent 运行时、项目初始化器或固定工程师生成器。

主 Agent 负责目标澄清、Plan、批注整理、实施编排、审查结果消费和最终对账。子 Agent 只执行有界单元、测试或独立审查，并以结构化结果回传。

本文件是索引。进入某个阶段时，只读取该阶段链接的参考文档；不要在冷启动时加载全部资源。

## 快速入口

### Tier 1

单一、有界、低风险任务只填写：

```yaml
goal: <要完成什么>
acceptance: <一条命令或一个可观察检查>
forbidden:
  - <不得发生的效果>
```

先读取 [Tier 1 模板](templates/PLAN-LITE.md)。默认流程是：一个实施 Agent、最小验收、独立 Spec Review、主 Agent 汇总。没有独立 Reviewer 时必须标记降级或不可用。

### 完整模式

出现升级触发器时，读取 [Plan 对话与批注](references/plan-dialogue.md)，生成完整 Plan；批准后再读取 [Spec 编译](references/spec-compiler.md) 和 [动态编排](references/orchestration.md)。

## 主流程

```text
主对话理解目标
  -> 生成 Plan 初稿
  -> Grill 提问并集中写入批注区
  -> 用户选择、补充或拒绝
  -> 主 Agent 整理并继续提问
  -> 所有必需缺口敲定
  -> 用户批准实施
  -> Tier 1 直接加工，或编译完整 Cycle Spec
  -> 主 Agent 动态分派有界任务
  -> 按风险执行 Review
  -> 构建/编译和独立测试（适用时）
  -> 主 Agent 对账并写结果
  -> 用户选择是否回溯优化
```

## 必须遵守的主规则

1. 未经用户批准，不实施、不发布、不执行不可逆操作。
2. Plan 是本轮意图权威；Cycle Spec 只能从批准 Plan 编译。
3. 子 Agent 只读取当前任务需要的最小上下文，不回灌完整过程。
4. 实施、Review、Test 和批准不得由同一身份自证完成。
5. 模型自述不能代替实际 Artifact、测试结果或可观察 Evidence。
6. 缺证据、范围漂移、审查失败或能力缺失时，返回 `revise`、`planning_review`、`blocked` 或 `not_available`，不能写成 `done`。
7. 失败审查、旧 Plan、返工和候选必须保留。

## Plan 批注门

所有待澄清问题集中在 Plan 的 `annotations` 区，使用 [Plan Annotation Schema](schemas/plan-annotation.schema.json) 和 [批注模板](templates/PLAN-ANNOTATION.md)。

主 Agent 必须先提出问题，再等待用户填写；收到回答后先整理批注和 Plan 版本，再重新检查缺口。只有以下条件同时满足，才可以反馈“准备实施”：

- 必填批注均为 `accepted`、`rejected` 或 `resolved`；
- 用户的选项或 `other` 已写入；
- 目标、范围、依赖和验收没有矛盾；
- 高风险未决项已经由用户决定；
- 当前 Plan 版本可通过对应 Schema。

“准备实施”只表示规划收敛，不表示用户已经批准；批准是单独的决定。

## 升级触发器

| 触发器 | 升级内容 |
|---|---|
| 多于一个单元或共享接口/Schema | 完整 Work Unit 表、依赖和 Cycle Spec |
| 核心行为、权限、迁移、公开 API 或发布 | 当前单元 Code Review 必做，再做 Spec Review |
| 同一问题返工达到 2 次 | 冻结 Spec、指纹和返工单元 |
| 主上下文压缩、跨上下文或恢复 | Trace、Work Log、checkpoint |
| 删除、资金、迁移或发布等不可逆效果 | 用户批准门和指纹 |
| 外部 API、凭据、网络或付费模型 | provider/data access gate |

未触发时保持 Tier 1，不补齐完整文书。

## Review 顺序

完整规则见 [Review 与 Test](references/review-and-test.md)。默认不并行：

```text
重要代码：Code Review -> 通过后 Spec Review
非重要代码：记录跳过 Code Review 的理由 -> Spec Review
```

Code Review `revise/blocked` 时短路，不启动 Spec Review。没有独立上下文时必须记录 `manual_reviewer`、`main_degraded` 或 `not_available`。

## 阶段索引

| 阶段 | 读取 |
|---|---|
| 生成 Plan、Grill 提问、批注整理、用户批准 | [references/plan-dialogue.md](references/plan-dialogue.md) |
| 完整 Plan 编译 Cycle Spec | [references/spec-compiler.md](references/spec-compiler.md) |
| Git/接口/并行/模型/上下文和子 Agent 分派 | [references/orchestration.md](references/orchestration.md) |
| Code Review、Spec Review、构建和独立测试 | [references/review-and-test.md](references/review-and-test.md) |
| Trace、Work Log、回溯和 SkillOpt | [references/trace-and-retro.md](references/trace-and-retro.md) |
| 运行产物目录和命名 | [references/storage-layout.md](references/storage-layout.md) |
| 跨文件引用、依赖和指纹语义检查 | [references/semantic-checks.md](references/semantic-checks.md) |
| 高风险完整治理原则 | [references/full-governance.md](references/full-governance.md) |
| 用户确认的策略决定 | [references/decision-record.md](references/decision-record.md) |

可选离线自检：

```text
python scripts/validate.py --root <loop-flow-root> --require-jsonschema
```

需要批准指纹时只使用：`python scripts/validate.py --fingerprint-plan <plan.json>`。不得手填或心算哈希。

脚本不是运行时硬依赖。缺少 `jsonschema` 时会明确报告降级，不得把结构检查写成完整 Schema 验证。

## 宿主适配

Codex、Claude Code、Pi、Zed、Qoder 等只需加载同一份 `SKILL.md`。宿主提供子 Agent、工具和可选 Hook；Loop Flow 定义 Plan、批注、任务边界、Review、Evidence 和用户批准。宿主不支持某能力时必须诚实降级。

## 结束状态

- `done`：适用的 Plan/Spec、Review、测试和用户决定均满足；
- `revise`：当前范围内存在可修复 Finding；
- `planning_review`：需要用户补充或裁决；
- `blocked`：外部权限、环境或安全边界阻断；
- `not_available`：Plan 明确允许的能力未启用。
