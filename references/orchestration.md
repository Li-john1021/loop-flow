# 动态编排

本文件在 Cycle Spec 已冻结，或 Tier 1 需要执行时加载。

## 环境嗅探

先读取低风险事实，再请求用户申报：

- `.git` 或 Git 探针成功：提出 `git_mode=optional`；否则 `none`，除非用户明确要求 Git；
- `pyproject.toml`、`package.json`、`Cargo.toml`、`go.mod`、`Makefile` 或测试配置：提出可执行 test/build 候选；
- 共享接口、Schema、迁移目录或多模块边界：默认需要接口合同；无法判断则 `planning_review`；
- 宿主报告 subagent、parallel、Hook 和 usage 能力时才启用；没有报告就按串行、手动和 usage unavailable 处理。

探测是默认值，不覆盖用户决定；依据写入 Work Log 或 Trace（完整模式）。

## 动态分派

主 Agent 不生成永久工程师。每个单元临时选择：

```yaml
role_type: implementer | specialist | tester | reviewer
model_tier: frontier | balanced | economy | user_selected
context_refs: <当前单元必要材料>
acceptance_refs: <对应验收>
stop_conditions: <停止条件>
```

需要分析模型匹配时，在 Task Envelope 和 `unit_dispatched` Trace 中记录 `capability_requirements`、`capability_source`、`selection_reason` 和 `expected_model_tier`；完成或失败事件在宿主可提供时补 `actual_model_id`、`attempts` 和 `usage`。这些字段记录选择事实，不代表已经证明模型能力。

主 Agent 保留全局目标和决策；实施 Agent 只消费单元上下文，回传 Artifact、Evidence、Status 和 Usage（可用时）。

## 并行规则

只有单元之间没有写路径冲突、共享接口依赖或验证顺序依赖时才并行。接口、Schema、权限、迁移和发布边界默认串行。没有子 Agent 时使用串行退化，并降低验证等级。
