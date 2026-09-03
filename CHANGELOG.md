# loop-flow 变更记录

## Unreleased

- 增强 Trace 字段以记录能力需求、模型选择事实和显式根因提示。
- 增加离线 Trace Consumer 和 `optimization-candidate` 合同，未知根因只产生证据缺口。
- 增加能力不匹配、Prompt、分段、流程和环境问题的候选评估规则；不自动修改 Skill。
- 将 `retro` 明确改为用户显式触发的高级模型异步 Consumer；周期结束只提醒，不自动消费 Trace。

## 0.1.0-alpha.2 - 2026-09-03

- 将 `SKILL.md` 重构为渐进式索引，补充分阶段参考文档和固定 Plan 批注合同。
- 增加跨平台 `INSTALL.md`、共用 `commands/` 命令清单和薄转发提示词。
- 增加显式 `spec` 冻结入口，要求完整模式先签署 Plan、冻结 Cycle Spec，再由 `run` 执行。
- 增加 `.loop-flow/` 运行产物布局、批注门、指纹 CLI、命令清单校验和 stale Spec 检查。
- 放宽下游 ID 编号校验，支持三位以上数字编号。
- 增加公开 CI 和校验器单元测试，覆盖假指纹、批注门、依赖环、stale Spec 和高编号 ID。
- 增加可选 Trace Consumer、能力选择记录和优化候选合同；`retro` 先消费事实，再进入独立评估和用户批准。

## 0.1.0-alpha.1 - 2026-09-03

- 首次发布轻量主对话编排 Skill，项目名称为 `loop-flow`。
- 增加 Tier 1 三字段任务卡和触发式晋升路径。
- 增加 Plan、Cycle Spec、Task、Review、Test、Trace 和 Work Log Schema。
- 增加 Codex、Claude Code 和通用宿主适配说明。
- 增加可选离线 `validate.py`，支持指纹、引用闭合、依赖环和 Review 策略检查。
- 采用 MIT License，允许修改、商用、再分发和二次集成。
