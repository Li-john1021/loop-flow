# Test Report：<test-id>

```yaml
schema_version: "1.0"
test_id: test:<id>
tester: tester:<id>
tester_context_ref: context:test:<id>
implementation_actor_refs:
  - worker:<id>
candidate_ref: <候选引用或指纹>
candidate_fingerprint: sha256:<64 hex>
mode: independent_subagent
verdict: pass
commands:
  - command: <实际命令>
    workdir: <工作目录>
    exit_code: 0
    passed: 0
    failed: 0
coverage: []
state_changes: []
evidence: []
unresolved: []
next_action: <下一步>
```

`tester` 不得等于 `implementation_actor_refs` 中任一身份；测试 Agent 必须读取当前候选和批准 Spec，而不是只读取实施总结。
