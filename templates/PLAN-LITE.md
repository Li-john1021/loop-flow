# Tier 1 Plan：<目标>

适用于一个有界、低风险、可快速验证的任务。填写三项即可开始：

```yaml
schema_version: "1.0"
plan_id: plan:<slug>
plan_version: 1
mode: tier1
goal: <要完成什么>
acceptance: <一条命令或一个可观察检查>
forbidden:
  - <不得发生的效果>
```

默认行为：主 Agent 直接把这张卡同时作为本轮 Spec 和 Task Envelope，选择一个实施 Agent，加工后执行最小验收，再由一个独立于实施 Agent 的 Spec Reviewer 异步审查。若宿主没有独立审查能力，必须明确选择 `review_executor=main_degraded` 或 `review_mode=none`，并在结果中标记降级；未触发升级前，不要求完整 Requirements、Cycle Spec、Code Review、指纹或发布门。Tier 1 的 Spec Reviewer 必须是独立子 Agent；无法提供时只能走降级或 `not_available`，不能由实施 Agent 自审。

可选状态字段：`review_mode=single_async`、`review_executor=independent_subagent`、`test_mode=manual`、`rework_count=0`、`annotations=[]`。如需提问，批注必须使用 [Plan Annotation 模板](PLAN-ANNOTATION.md)；这些字段不属于三字段冷启动必填项。

## 触发式升级

| 触发条件 | 增加的合同 |
|---|---|
| 多于一个单元，或触碰共享接口 | Work Unit 表和依赖顺序；必要时晋升完整 Plan/Cycle Spec |
| 代码涉及权限、迁移、公开 API、核心行为或发布 | `code_impact=critical/material`，先 Code Review，再 Spec Review |
| 同一问题返工达到 2 次 | 冻结 Cycle Spec、候选指纹和新的返工单元；递增 `rework_count` |
| 主对话上下文将压缩、跨上下文或需要恢复 | Trace、Work Log 和 checkpoint |
| 用户资金、删除、迁移、发布等不可逆效果 | 用户批准门和指纹 |
| 外部 API、凭据、网络或付费模型 | provider/data access gate |

未触发条件时，保持 Tier 1；不为了形式填满重型文书。触发后，保留已有 `plan_id`、goal、acceptance 和 forbidden，补齐完整 Plan/Cycle Spec，不重新发明一套任务。
