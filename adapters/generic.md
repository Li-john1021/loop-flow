# 通用宿主适配

只要宿主支持以下三个动作即可接入：

1. 加载 `SKILL.md` 与所需 Schema/模板。
2. 创建有界子任务并传入 Task Envelope。
3. 保存和回传符合合同的结构化结果。

缺少并行、Hook、自动测试、模型 usage 或文件指纹能力时，不得伪造能力；选择 `serial/manual/not_available`，Review 报告中的 `review_executor` 选择 `manual_reviewer` 或 `main_degraded`，并在 Trace 与 Work Log 中记录退化原因。
