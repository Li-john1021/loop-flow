# Plan：<项目目标>

状态：`draft`
Plan ID：`plan:<slug>`
版本：`1`
所有者：`<user>`

canonical `plan_fingerprint` 请直接运行 `python scripts/validate.py --fingerprint-plan <plan.json>`；该命令会移除 `approval` 与 `plan_fingerprint` 后再计算 SHA-256。批准文件中的 `approved_plan_fingerprint` 必须等于命令输出。

## 目标

- 目标：
- 成功定义：
- 用户价值：

## 当前问题与上下文

- 问题：
- 当前状态：
- 事实来源：
- 已知约束：

## 范围

### 范围内

-

### 范围外

-

## Requirements

| ID | 优先级 | 原子要求 | 来源 |
|---|---|---|---|
| REQ-001 | must |  |  |

## Deliverables

| ID | 类型 | 描述 | 位置/目的地 |
|---|---|---|---|
| OUT-001 |  |  |  |

## Acceptance

| ID | 证明 Requirement | 检查方法 | Evidence 类型 | 停止条件 |
|---|---|---|---|---|
| AC-001 | REQ-001 |  | test/artifact/review/manual_confirmation/build/trace |  |

## 决策与未决问题

| ID | 问题 | 当前状态 | 决定/需要用户回答 |
|---|---|---|---|
| DEC-001 |  | open |  |

## 执行政策

- 编排入口：`main_dialogue_skill`
- Git：`none / optional / required`
- 工作区：`single_workspace / isolated_paths / isolated_worktree`
- 接口：`none / existing_contract / new_contract / unknown`
- 并行：`serial / parallel_safe_units / conditional`
- 最大并行单元：
- 上下文策略：
- 规划模型：`frontier / balanced / economy / user_selected`
- 实施模型：`frontier / balanced / economy / user_selected`
- 审查模型：`frontier / balanced / economy / user_selected`

## 质量政策

- Review 模式：`sequential_conditional`（两个 Review 不并行，按下方顺序执行）
- Review 执行者：`independent_subagent / manual_reviewer / main_degraded`
- 代码影响：初稿填写 `unknown`；具体影响在 Work Unit 形成后判定
- Code Review：初稿填写 `deferred`；具体策略在 Work Unit 形成后判定
- Code Review 决策理由：`<初稿可留空；单元形成后必填>`
- 规则：`critical/material -> required`；`limited -> optional`；`none -> not_applicable`
- 测试：`independent_subagent / manual / not_available`
- 构建：`required / when_applicable / not_applicable`
- Trace：`canonical_minimal / canonical_detailed / manual_log`
- 回溯：`user_opt_in / required / none`

## Risks

| ID | 风险 | 影响 | 缓解 | 负责人 |
|---|---|---|---|---|
| RISK-001 |  | low/medium/high/critical |  |  |

## 用户批注

批注必须使用 [Plan Annotation 模板](PLAN-ANNOTATION.md) 和 `schemas/plan-annotation.schema.json`。所有待决问题集中在这里；一条批注只表达一个问题。

```yaml
annotations: []
```

主 Agent 先列出全部必要问题并等待用户回答；不能把未回答问题隐藏到正文，也不能在必填批注仍为 `open/answered` 时请求实施批准。

## 批准

```yaml
status: not_requested
approved_by:
approved_at:
approved_plan_fingerprint:
decision_note:
```

只有 `status=approved` 时才允许填写批准者、时间和指纹。
