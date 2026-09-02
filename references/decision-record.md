# 用户决策记录

## DEC-001：分级 Review 采用串行条件模式

日期：2026-09-03
决策者：用户
状态：已确认

用户确认以下 Review 策略为本 Skill 的正式质量策略：

```text
重要代码：Code Review -> 通过后再做 Spec Review
非重要代码：记录跳过 Code Review 的理由 -> Spec Review
```

Code Review 与 Spec Review 不并行。Code Review 返回 `revise/blocked` 时，不启动 Spec Review，先返工或暂停。代码影响在 Work Unit 形成、实际变更可观察后判断，不在冷启动 Plan 阶段猜测。

该决定替代早期“两个异步 Review 并行”的审查基准，属于用户批准的产品策略演进，不是未解决缺陷。

## DEC-002：轻量 Tier 1 为默认入口

日期：2026-09-03
决策者：用户
状态：已确认

单一有界低风险任务默认使用 `goal/acceptance/forbidden` 三字段卡。只有触发器命中时才晋升完整 Plan、Cycle Spec、Trace、指纹和额外 Review。
