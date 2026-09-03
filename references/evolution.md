# 工作流进化

本文件在用户调用 `retro`、需要分析 Trace 或评估优化候选时加载。它定义候选如何从事实进入验证，不允许自动修改当前 Skill。

## 根因分类

| 分类 | 证据要求 | 候选方向 |
|---|---|---|
| `prompt` | 合同、工具和能力足够，但提示词缺少明确边界或验收 | 增加最小约束、允许路径、Acceptance 或停止条件 |
| `decomposition` | 单元过大、职责混杂或无法独立验收 | 拆分或合并 Work Unit |
| `workflow` | Review、测试、恢复或批准顺序不合适 | 修改当前周期规则 |
| `capability_mismatch` | 合同清楚、能力已声明或可观察，实际结果仍失败 | 升级模型、切换专职 Agent 或缩小单元 |
| `environment` | 权限、工具、依赖或外部服务阻断 | 补齐能力或诚实暂停 |
| `insufficient_evidence` | 缺少实际 Artifact、Evidence、退出码或能力声明 | 先补证据，不改全局流程 |

`root_cause_hint` 是待验证标签，不是自动证明。单次失败且没有明确提示时，Consumer 必须输出证据缺口，不能猜测根因。

## 能力不匹配门

只有同时满足以下条件，才允许提出 `capability_mismatch`：

1. Work Unit 的目标、禁止效果和 Acceptance 已明确；
2. 所需工具和上下文已可用，或有宿主/用户能力声明；
3. 实际 Artifact、退出码或测试结果证明失败；
4. 没有更直接的 Prompt、分段、流程或环境原因。

这类候选不评价模型好坏，只调整模型层级、专职角色或单元边界。

## 候选生命周期

```text
Trace JSONL
  -> 用户显式调用 retro
  -> 独立高级 Consumer/Judge
  -> scripts/consume_trace.py
  -> optimization-candidate(status=proposed)
  -> held-out + 对抗 + 回归 + 质量/成本检查
  -> 用户批准
  -> 新版本或 rejected/rolled_back
```

候选合同见 `schemas/optimization-candidate.schema.json`。旧 Skill、旧候选、失败报告和回滚事件必须保留。
