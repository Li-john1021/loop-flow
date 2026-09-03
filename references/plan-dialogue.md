# Plan 对话与批注

本文件在用户提出新目标、需要修改已有 Plan，或 Tier 1 命中升级触发器时加载。

## 1. 先判断模式

一个有界、低风险、单一任务默认使用 Tier 1；不要为了完整文书先问一堆问题。出现以下任一项时转完整 Plan：多单元/共享接口、核心代码或权限、两次返工、上下文恢复、不可逆效果或外部供应商。

## 2. Grill 提问

主 Agent 先用问题暴露缺口，不直接替用户作决定。问题应覆盖当前真正影响实施的项目：

- 目标：要改变什么，谁会使用，什么算成功？
- 范围：明确做什么、不做什么，是否存在时间或资源边界？
- 产物：交付什么格式，写到哪里，由谁消费？
- 约束：已有接口、兼容性、权限、数据、许可证或平台限制是什么？
- 执行：是否存在 Git、测试、构建、共享接口、并行安全边界或外部能力？
- 质量：哪些结果必须测试、Review、人工确认或用户批准？

只提与本轮目标有关的问题；每一条问题只解决一个缺口。

## 3. 批注区固定格式

所有问题集中写入 Plan 的 `annotations` 数组。使用 [Plan Annotation Schema](../schemas/plan-annotation.schema.json) 和 [批注模板](../templates/PLAN-ANNOTATION.md)。

```yaml
schema_version: "1.0"
annotation_id: ANN-001
plan_ref: plan:<slug>
plan_version: 1
target: /execution_policy/parallelism
question: 是否允许并行开发？
reason: 该决定会影响任务拆分、文件冲突和上下文隔离。
options:
  - id: A
    label: 串行
    value: serial
  - id: B
    label: 安全单元并行
    value: parallel_safe_units
answer: null
other: null
status: open
required: true
created_at: <ISO-8601>
```

状态含义：

- `open`：等待用户回答；
- `answered`：用户已选择或填写 `other`，主 Agent 尚未整理；
- `accepted`：回答已写入新 Plan 版本；
- `rejected`：用户拒绝给定选项并明确替代边界；
- `resolved`：主 Agent 已修改或答复，填写 `resolved_by` 和 `resolution_note`。

## 4. 整理循环

收到用户批注后，主 Agent 必须先读取全部批注，再做以下动作：

1. 将回答映射回目标字段；
2. 检查与范围、风险、依赖和 Acceptance 的冲突；
3. 生成递增 `plan_version`，保留旧版本和批注；
4. 把已处理批注标记为 `accepted/rejected/resolved`；
5. 对新发现的缺口追加下一批 `open` 批注。

只要存在必填的 `open/answered` 批注、关键冲突或不可验证 Acceptance，就继续提问。不能说“准备实施”。

当必填缺口全部关闭、Plan 可验证且没有高风险未决项时，主 Agent 才反馈“准备实施”，然后单独询问用户是否批准实施。准备实施不等于已批准。

## 5. Tier 1 批注

Tier 1 仍只要求 `goal/acceptance/forbidden` 三字段。若对话中出现不确定事项，可以增加可选 `annotations`；`rework_count` 每形成一次返工递增，达到 2 时晋升完整模式。Tier 1 的批注不要求完整 Trace，但必须保留主对话摘要和用户回答。
