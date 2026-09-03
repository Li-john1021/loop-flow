# 运行产物布局

本文件在任务需要持久化运行记录、跨上下文恢复或用户要求查看证据时加载。它定义默认布局，不要求宿主安装运行时。

```text
.loop-flow/
├── plans/       # Plan 初稿、批注整理后的版本和批准快照
├── cycles/      # 完整模式编译出的 Cycle Spec
├── reviews/     # Code Review、Spec Review 报告
├── tests/       # 独立测试报告和测试 Evidence 索引
├── trace/       # 追加式 Trace 事件
├── work-logs/   # 面向用户的周期摘要
├── decisions/   # 用户裁决和回溯决定
└── checkpoints/ # 跨上下文恢复所需的最小检查点
```

文件名使用 `<kind>-<slug>-v<version>.<ext>`；Trace 事件使用当前工作区或周期命名空间，避免跨周期重号。一次运行不得覆盖旧 Plan、报告、Trace 或检查点；修复应写入新版本并保留引用关系。

`.loop-flow/` 默认在 `.gitignore` 中忽略。若用户需要提交可复核证据，应先脱敏并由用户明确选择要纳入版本控制的文件；不得把密钥、完整 Prompt、推理或私人 transcript 写入其中。
