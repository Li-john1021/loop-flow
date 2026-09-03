# Plan Annotation：<问题标题>

主 Agent 在 Plan 批注区为每个缺口生成一条记录。用户只需选择一个选项、填写 `other`，或明确表示暂时无法决定。

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
  - id: C
    label: 条件并行
    value: conditional
answer: null
other: null
status: open
required: true
created_at: <ISO-8601>
```

## 状态

- `open`：主 Agent 已提出问题，等待用户回答。
- `answered`：用户已选择 `answer` 或填写 `other`，主 Agent 尚未整理进 Plan。
- `accepted`：主 Agent 已将回答写入新 Plan 版本，问题的结论被采纳。
- `rejected`：用户明确拒绝所有给定方案，必须在 `other` 或对话中说明替代边界。
- `resolved`：主 Agent 已完成修改或答复，填写 `resolved_by`、`resolution_note`。

只有 `accepted`、`rejected` 或 `resolved` 才能关闭必填缺口。`open` 或 `answered` 仍然阻止“准备实施”。

## 批注规则

1. `target` 使用 Plan 的字段路径；不要把多个独立问题塞进一条批注。
2. 每条必填批注至少提供两个互斥选项；开放式问题仍保留 `other`。
3. 用户回答不能直接覆盖旧 Plan；主 Agent 必须生成递增 `plan_version` 并保留批注。
4. 回答与已有约束冲突时，回到主对话继续提问，不替用户裁决。
5. 所有必填批注关闭、目标/范围/验收无冲突后，主 Agent 才能请求实施批准。
