# Trace、Work Log 与回溯

本文件在任务触发 Trace、上下文恢复，或用户要求回溯时加载。

## Trace

完整模式的 Trace 是最小追加式事件记录，至少包含：Plan/Spec 版本、Work Unit、角色、模型层级、上下文引用、Artifact/Evidence/Review/Test 引用、状态、退出码、用量（可用时）、返工、checkpoint 和用户决定。需要分析分段和模型选择时，补充 `capability_requirements`、`capability_source`、`selection_reason`、`expected_model_tier`、`actual_model_id`、`attempts` 和 `root_cause_hint`。事件 ID 使用工作区或周期命名空间，避免跨周期冲突。默认不保存完整 Prompt、推理或 transcript。

指纹只在升级触发器要求时计算，使用 `python scripts/validate.py --fingerprint-plan <plan.json>` 这一唯一命令；不可计算时写 `fingerprint_status=unavailable`，不得手填哈希。

## Work Log

Work Log 是面向用户的摘要，不是第二套事实源。完整模式的每条单元、审查、测试和决定都引用 Trace event ID；Tier 1 只需保留任务卡、验收观察、Spec Review 结果、未决问题和用户决定。

## 回溯

周期完成后先询问用户是否回溯。用户同意后，先由 `scripts/consume_trace.py` 读取脱敏 Trace，生成事实摘要和 `optimization-candidate`；再由独立 Consumer/Judge 评估根因。候选只能提出：上下文压缩、模型分层、任务拆分、Review 规则和提示词的候选改动。候选必须经过 held-out、对抗测试、质量/成本门禁和用户批准。

消费者不得从单次失败的自然语言 `reason` 推断因果。没有显式 `root_cause_hint` 或缺少实际 Evidence 时，报告 `insufficient_evidence`，不提出全局修改。`capability_mismatch` 只表示合同清楚、能力已声明或可观察、且实际结果仍失败的待验证假设，不是对模型的评价。

发布新 Skill 版本时保留上一版本；出现质量回归、错误放行、成本异常或用户明确否决时，提出回滚并等待用户批准。回滚写入 `optimization_rolled_back` 事件，旧版本不得删除。
