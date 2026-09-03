# Codex 宿主适配

## 最小能力

Codex 只需要让主对话加载 `SKILL.md`，并能根据 Task Envelope 创建或调用子 Agent。子 Agent 的输出必须保存为 Unit Result、Review Report 或 Test Report，主对话消费引用和结构化字段。

## 分派规则

- 支持 subagent/parallel 时，只有 `parallelism=parallel_safe_units` 且路径、接口、依赖和验证边界均不冲突才并行。
- 不支持 subagent 时，按相同顺序串行执行，并写入 `capability=serial_fallback`。
- Review 结果必须记录 `review_executor=independent_subagent`；无独立上下文时改为 `manual_reviewer` 或 `main_degraded`，不得声称独立审查。
- 主对话不把子 Agent 完整 transcript 复制回上下文。
- 模型选择按 Task Envelope 的 `model_tier` 执行；无法提供准确 usage 时标记 `usage_unavailable`。

## 不可替代项

Codex 的子 Agent API 不能替代 Plan 批准、Schema 校验、Review 独立性、Test Agent 和用户最终决定。

## 命令映射

Codex 没有假定存在的通用斜杠命令注册表。可用 `$loop-flow` 加命令参数转发到同一份命令清单：

```text
$loop-flow plan
$loop-flow annotate
$loop-flow ready
$loop-flow approve
$loop-flow run all
$loop-flow status
$loop-flow validate
$loop-flow resume
$loop-flow retro
$loop-flow cancel
```

若当前 Codex 宿主不支持参数化 Skill，则用自然语言表达相同命令；不得为命令缺失创建第二套状态机。
