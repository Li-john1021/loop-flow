# 命令层契约

本文件定义平台无关的命令语义。具体清单和薄提示词位于 `commands/manifest.json` 与 `commands/prompts/`。Claude Code、Codex、Gemini CLI 或其他宿主可以把它映射为斜杠命令、Skill 参数或自然语言；不得复制一套独立流程。

## 用户命令

| 命令 | 层级 | 作用 | 门控 |
|---|---|---|---|
| `plan` | 核心 | 根据当前讨论生成或更新 Plan；首次需要持久化时创建 `.loop-flow/` | 不实施；更新递增 `plan_version` 并保留旧版 |
| `annotate` | 核心 | 展示待答批注，吸收用户选择/`other`，生成新 Plan 版本并报告剩余缺口 | 不改变批准状态 |
| `ready` | 核心 | 执行 Schema、语义和批注门检查 | 只读；`ready_for_approval` 不等于批准 |
| `approve` | 核心 | 记录用户明确批准 | 必须用户确认；仅在策略要求时校验指纹 |
| `run [WU-id\|--step\|all]` | 核心 | 批准后启动完整链路，默认执行 `all` | 未批准拒绝；单步不能跳过 Review、测试或安全门 |
| `status` | 核心 | 查看 Plan、周期、阻断和最近 Evidence 摘要 | 只读，不回显完整 Prompt/transcript |
| `validate` | 核心 | 执行 Schema、引用、依赖、批注和指纹校验 | 只读；缺少校验器时诚实标记降级 |
| `resume` | 恢复 | 从中断、checkpoint 或 `blocked` 状态继续 | 重新检查范围、批准和能力边界 |
| `retro` | 收尾 | 请求回溯并提出优化候选 | 仅周期结束后可用，需用户决定是否采纳 |
| `cancel` | 生命周期 | 取消当前 Plan 或周期 | 保留全部历史，不删除失败证据 |

## 关键语义

1. `plan` 不是“收到请求就直接生成”。主对话先进行必要讨论，再生成可带未决 `annotations` 的 Plan 初稿。
2. `annotate` 可以在同一命令中展示问题和吸收回答；只要必填批注仍为 `open/answered`，就不能进入 `ready_for_approval`。
3. `approve` 永远是用户动作。Tier 1 默认不需要指纹；晋升、不可逆效果或返工冻结时，使用 `python scripts/validate.py --fingerprint-plan <plan.json>` 计算并校验。
4. `run` 是无感串联入口。它内部按适用性执行 Spec 编译、分派、Code Review、Spec Review、构建、测试、对账和 Trace；用户不必逐阶段输入命令。
5. `run --step` 只用于调试或恢复一个已授权步骤，不能改变既定 Review 顺序、跳过测试或扩大路径。
6. `validate` 失败返回 `revise`、`planning_review` 或 `blocked`，不能包装成 `done`。

## 不对用户暴露的内部动作

`compile-spec`、`dispatch`、`code-review`、`spec-review`、`build`、`test`、`audit` 和 `trace` 是 `run` 的内部阶段。宿主可为排障提供别名，但别名必须转发到本契约，不能另建状态机。

## 宿主映射

- Claude Code：可用 `/loop-flow plan`、`/loop-flow run` 等 Skill 参数；也可继续自然语言触发。
- Codex：可用 `$loop-flow` 加命令参数或自然语言。
- Gemini CLI：使用其 Skill 发现和命令入口映射。
- 其他宿主：至少保留 `plan`、`annotate`、`approve`、`run`、`status`、`resume` 的自然语言降级。
