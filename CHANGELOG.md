# loop-flow 变更记录

## 0.1.0-alpha.1 - 2026-09-03

- 首次发布轻量主对话编排 Skill，项目名称为 `loop-flow`。
- 增加 Tier 1 三字段任务卡和触发式晋升路径。
- 增加 Plan、Cycle Spec、Task、Review、Test、Trace 和 Work Log Schema。
- 增加 Codex、Claude Code 和通用宿主适配说明。
- 增加可选离线 `validate.py`，支持指纹、引用闭合、依赖环和 Review 策略检查。
- 增加跨平台 `INSTALL.md`，明确 Skill 安装、更新、smoke check 和 Python 可选依赖边界。
- 固化平台无关命令契约，明确 `plan -> annotate -> ready -> approve -> run` 与批准后的无感串联。
- 增加 `commands/` 共用命令清单和薄转发提示词，并补充 Claude Code、Codex、Gemini CLI 映射说明。
- 采用 MIT License，允许修改、商用、再分发和二次集成。
