# Unit Result：<WU-ID>

```yaml
schema_version: "1.0"
result_id: result:<id>
unit_ref: WU-001
actor: worker:<id>
status: pass
artifacts: []
evidence: []
checks: []
unresolved: []
next_action: <下一步>
```

每个 Evidence 必须包含实际命令、工作目录、退出码或实际文件观察。每个 Artifact 必须有路径或引用和内容指纹。Usage 可用时记录 provider、model、model_tier、input/output tokens、总 tokens、cost 和 duration。
