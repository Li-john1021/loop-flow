# Trace、Work Log 与回溯

本文件在任务触发 Trace、上下文恢复，或用户要求回溯时加载。

## Trace

完整模式的 Trace 是最小追加式事件记录，至少包含：Plan/Spec 版本、Work Unit、角色、模型层级、上下文引用、Artifact/Evidence/Review/Test 引用、状态、退出码、用量（可用时）、返工、checkpoint 和用户决定。事件 ID 使用工作区或周期命名空间，避免跨周期冲突。默认不保存完整 Prompt、推理或 transcript。

指纹只在升级触发器要求时计算，使用 `python scripts/validate.py --fingerprint-plan <plan.json>` 这一唯一命令；不可计算时写 `fingerprint_status=unavailable`，不得手填哈希。

## Work Log

Work Log 是面向用户的摘要，不是第二套事实源。完整模式的每条单元、审查、测试和决定都引用 Trace event ID；Tier 1 只需保留任务卡、验收观察、Spec Review 结果、未决问题和用户决定。

## 回溯

周期完成后先询问用户是否回溯。用户同意后，Harness Engineer 或 SkillOpt 只能提出：上下文压缩、模型分层、任务拆分、Review 规则和提示词的候选改动。候选必须经过 held-out、对抗测试、质量/成本门禁和用户批准。

发布新 Skill 版本时保留上一版本；出现质量回归、错误放行、成本异常或用户明确否决时，提出回滚并等待用户批准。回滚写入 `optimization_rolled_back` 事件，旧版本不得删除。
